# Prompt for Codex (build a Nobel Prize Prediction application)

You are an expert software engineer + data scientist. Build a production-grade web app that predicts the next Nobel Prize laureates (Physics, Chemistry, Physiology/Medicine, Economics) with transparent explanations.

## 0) Tech stack

* Backend: **Python 3.11**, **FastAPI**, **uvicorn**, **Pydantic**, **SQLAlchemy**.
* Data/ETL: **Airflow** (or **Prefect** if simpler), **DuckDB** for staging, **PostgreSQL** for prod, **MinIO/S3** for raw dumps, **Great Expectations** for data QA.
* Modeling: **scikit-learn**, **xgboost**, **lightgbm**, **statsmodels** (for survival/time-to-award baselines), **shap** for explainability.
* Frontend: **React + Vite**, **Material UI**; charts with **Plotly**.
* Infra: Docker Compose; `.env` for secrets; simple role-based auth.
* Testing: pytest; add CI workflow (GitHub Actions) for lint/test.

## 1) Problem framing

* Goal: output, each September–October, a **ranked shortlist** per field with **calibrated probability of winning this cycle**, plus a 3-year horizon.
* Training target: whether a scientist eventually wins a Nobel in a field (label), with **time-to-event** to enable hazard/probability for a given year.

## 2) Data ingestion (automate with scheduled DAGs)

Implement robust, cached connectors and schema for:

**A. Bibliometrics & authors**

* **OpenAlex** API: works, institutions, authors, citations, fields of study; collect yearly citation counts, field-normalized citation rate, top-1% paper share, co-citation/coauthor graphs.
* **Crossref** (backup for DOIs, years, venues).
* **Semantic Scholar** (rate-limited; store paper-level influence if accessible).
* Import **Clarivate Citation Laureates** (scrape latest page; keep historical lists) as a binary/ordinal feature. ([Research Professional News][2])

**B. Awards & proxies**
Structured scrapers/parsers for:

* **Lasker (Med)**, **Wolf (Phy/Chem/Med)**, **Breakthrough (Life/Physics/Math)**, **Kavli**, **Turing (for Econ/Phys if AI-related)**, **Gairdner**, **Copley**, **National Academy elections**. One-hot and lag features: years-since-award, count of major awards, award network centrality.

**C. Topic heat & zeitgeist**

* Build yearly **topic models** (BERTopic or LDA) on OpenAlex abstracts per field; compute trend slopes (last 5–10 years).
* Add **media momentum** proxies: Wikipedia page views for candidates; news mentions (GDELT/NewsAPI if available); normalize by field.

**D. Nobel ground truth**

* Scrape **NobelPrize.org** for all winners + year + “scientific contribution” text; map to fields and topics; create positive labels and award-year. (Store committee text for later keyword matching.)

**E. Historical nominations (limited)**

* Where public (e.g., up to ~1974 Chem/Phys, ~1953 Med), use as features for older cohorts only; mark coverage gap (feature mask). (This is known to be partially available only; keep it optional.) ([SSRN][3])

**F. Author disambiguation**

* Use OpenAlex author IDs as spine; add string-match fallback; build deterministic merge rules + probabilistic (tf-idf over affiliations/venues) with human-review queue.

## 3) Feature engineering

Create per-author-per-year feature vectors, lagged to maintain causality:

* **Influence & momentum**

  * Total citations, **field-normalized citations** (percentile), **5-year moving average** and **year-over-year ?**.
  * **h-index**, **g-index**, **m-quotient** (h / career length), **top-decile paper share**, **Highly Cited Papers** proxy (OpenAlex percentile).
  * **Coauthor network centrality** (PageRank, betweenness); **co-citation** centrality.
  * **Seminal-paper indicator**: top-0.1% cited in a subfield; time since that paper.

* **Awards & recognition**

  * Binary flags for each major award; recency; count; sequences (e.g., Lasker?Nobel path).
  * Academy memberships; keynote frequency (if scrappable).

* **Topic alignment**

  * Cosine similarity between author’s topic vector and **committee citation text** embeddings for recent Nobel awards in the same field.
  * **Topic trend slope** for author’s dominant topic cluster.

* **Career arc & demographics (coarse)**

  * Career age, institution prestige (OpenAlex institution citations per capita).
  * **Geography** at time t (region dummies).
  * (No sensitive personal attributes beyond public affiliation/country.)

* **Meta**

  * Clarivate Citation Laureate flag; **presence in expert prediction lists** (C&EN, ChemistryWorld) as weak signals; keep as optional boolean with low model weight. ([Chemical & Engineering News][4])

## 4) Modeling

Implement three complementary estimators:

1. **Gradient-Boosted Trees (XGBoost/LightGBM)** on last-available-year features ? output **P(win in next 3 years)** and **P(win this year)**.
2. **Regularized Cox PH** and **Random Survival Forests** for time-to-award hazard; convert to year-specific probabilities.
3. **Logistic baseline** with elastic net for interpretability.

* **Calibration**: Platt/Isotonic per field; reliability plots stored.
* **Explainability**: SHAP values per candidate; surfaced in UI.

## 5) Backtesting & evaluation

* Backtest from **1980?2024** rolling-origin, predicting each October given data available up to Sept 30 of that year.
* Metrics: **Hit@k** (did the actual laureate appear in top-10/20 shortlist in the correct field?), **AUC-PR**, **Brier score** (calibration), **lead time** (years between first appearance at ?10% and win).
* Compare to:

  * **Naïve citation rank** baseline.
  * **Clarivate Citation Laureates** shortlist overlap.
* Save evaluation dashboards and CSVs.

## 6) Application UX

* Landing page: pick field + year; show **Top 20 candidates** with:

  * Headshot (Wikipedia/Wikidata), affiliation, **probability**, **SHAP top drivers**, key papers, award history.
  * Toggle **“this year” vs “3-year horizon”**.
* Candidate profile page:

  * Citation trajectory chart; award timeline; topic map; coauthor network mini-graph; “similar past laureates.”
* **What-if** sandbox: slider to simulate additional citations/awards to see probability sensitivity (SHAP-based).
* **Transparency**: show data sources & freshness; link to prior laureates.
* **Exports**: CSV, PDF report per field/year.

## 7) Data quality & governance

* Great Expectations checks: nulls, date monotonicity, ID uniqueness, API completeness.
* Provenance table: for every feature, store `source`, `as_of_date`, `latency_days`.
* PII policy: only public professional data.

## 8) Scheduling & freshness

* Nightly ETL for bibliometrics; weekly for awards; daily during Nobel week (late Sept–early Oct).
* Snapshots on **Sept 30** for “official” annual predictions.

## 9) Reproducibility

* Provide `make bootstrap` to stand up services and seed a **tiny toy dataset** + pretrained mini models so the app runs end-to-end without secrets.
* Jupyter notebooks: EDA, feature cookbook, model cards.

## 10) Deliverables

* Dockerized monorepo with `backend/`, `frontend/`, `etl/`, `models/`, `infra/`.
* Pre-commit hooks (black, isort, ruff, mypy).
* Seed **field: Physics** pipeline first; add Chemistry/Med/Econ after pattern proven.
* Include **model card** documenting limitations & ethical considerations (bias, geographic coverage, nomination secrecy).

## 11) Seed references to encode in README (as rationale)

* Fuoco, *How To Predict The Winners Of The Nobel Prize For 2025* (SSRN 5254426) — emphasizes citation patterns, nomination/award proxies, and AI-era topic heat. ([SSRN][1])
* Garfield, “Can Nobel Prize Winners Be Predicted?” — classic citation-based predictive framework. ([Garfield Library][5])
* Notes on nomination database coverage constraints (public up to mid-20th century; use cautiously). ([SSRN][3])
* Contemporary expert lists used only as weak features (C&EN webinar poll; ChemistryWorld data-driven picks). ([Chemical & Engineering News][4])

## 12) Stretch goals (if time permits)

* Ensemble with a **graph neural network** on coauthor/cocitation graphs (PyTorch Geometric).
* Integrate a **prediction-market feed** (if any exist for Nobels) and learn a meta-calibrator. ([ResearchGate][6])
* Add **LLM retrieval-augmented summaries** of “why now?” for each candidate pulling from papers and awards pages (citations shown).

---

### Acceptance criteria

* A developer can run `docker compose up`, visit `http://localhost:8000` (API) and `http://localhost:5173` (UI), and:

  1. trigger an ETL on a small seed (OpenAlex subset),
  2. train a baseline model,
  3. view a top-20 shortlist for Physics with probabilities and SHAP explanations,
  4. download a PDF/CSV report,
  5. see a backtest panel reporting Hit@10 and calibration for 2000–2020.
