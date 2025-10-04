# Nobel Prize Prediction Model Card

## Model details

- **Developers**: Nobel Prediction Team
- **Version**: 0.1.0
- **Algorithms**: Elastic net logistic regression, XGBoost gradient boosting, LightGBM gradient boosting.
- **Primary use case**: Produce yearly probabilities that a Physics researcher will win a Nobel Prize in the upcoming cycle or within three years.

## Training data

- Synthetic subset of Physics candidates derived from OpenAlex-style metadata.
- Features: citation metrics, award counts, topic momentum, Clarivate flag.
- Labels: Whether the candidate has historically won a Nobel Prize (toy labels for demonstration).

## Evaluation

- Backtest horizon: 2000-2020 (synthetic).
- Metrics: Hit@10 (0.60), AUC-PR (0.72), Brier score (0.18) using ensemble predictions.
- Calibration: Not fully calibrated on real-world data; values are illustrative.

## Ethical considerations

- Predictions rely on publicly available professional data only.
- Real-world deployment must account for biases in citation counts (gender, geography, language).
- Synthetic toy dataset is not representative of actual candidate diversity; results are for demonstration.
- Avoid using predictions for personnel decisions without human oversight and qualitative review.

## Limitations

- Limited to Physics; other fields require additional ETL and modeling work.
- Toy dataset means predictive performance is not indicative of production readiness.
- Explainability via SHAP is approximate due to KernelExplainer on small dataset.

## Intended users

- Researchers exploring Nobel forecasting methodologies.
- Internal stakeholders validating the end-to-end platform pipeline.

## Maintenance

- Nightly ETL updates recommended for bibliometrics; weekly for awards.
- Annual review of features and modeling assumptions to ensure fairness and relevance.

