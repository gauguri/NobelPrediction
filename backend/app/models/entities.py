from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    field: Mapped[str] = mapped_column(String, nullable=False, index=True)
    affiliation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    headshot_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    openalex_id: Mapped[Optional[str]] = mapped_column(String, unique=True)
    clarivate_laureate: Mapped[bool] = mapped_column(default=False)

    predictions: Mapped[list[Prediction]] = relationship("Prediction", back_populates="candidate")
    awards: Mapped[list[AwardEvent]] = relationship("AwardEvent", back_populates="candidate")


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = (
        UniqueConstraint("candidate_id", "prediction_year", "horizon", name="uniq_prediction"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    prediction_year: Mapped[int] = mapped_column(Integer, nullable=False)
    field: Mapped[str] = mapped_column(String, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    horizon: Mapped[str] = mapped_column(String, nullable=False, doc="one_year or three_year")
    shap_values: Mapped[dict] = mapped_column(JSON, default=dict)
    top_features: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="predictions")


class AwardEvent(Base):
    __tablename__ = "award_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    award_name: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="awards")


class BacktestMetric(Base):
    __tablename__ = "backtest_metrics"
    __table_args__ = (UniqueConstraint("field", "metric", name="uniq_metric"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    field: Mapped[str] = mapped_column(String, nullable=False)
    metric: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict)


class ProvenanceRecord(Base):
    __tablename__ = "data_provenance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feature_name: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    as_of_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    latency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

