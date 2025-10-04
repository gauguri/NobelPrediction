from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    openalex_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    field: Mapped[str] = mapped_column(String, nullable=False)
    affiliation: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=True)
    headshot_url: Mapped[str] = mapped_column(String, nullable=True)

    feature_snapshots: Mapped[list["FeatureSnapshot"]] = relationship(back_populates="candidate")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="candidate")


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    as_of_year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_citations: Mapped[int] = mapped_column(Integer, nullable=False)
    h_index: Mapped[float] = mapped_column(Float, nullable=False)
    recent_trend: Mapped[float] = mapped_column(Float, nullable=False)
    seminal_score: Mapped[float] = mapped_column(Float, nullable=False)
    award_count: Mapped[int] = mapped_column(Integer, nullable=False)

    candidate: Mapped[Candidate] = relationship(back_populates="feature_snapshots")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    horizon: Mapped[str] = mapped_column(String, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)

    candidate: Mapped[Candidate] = relationship(back_populates="predictions")
    shap_values: Mapped[list["ShapAttribution"]] = relationship(back_populates="prediction")


class ShapAttribution(Base):
    __tablename__ = "shap_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"))
    feature_name: Mapped[str] = mapped_column(String, nullable=False)
    feature_value: Mapped[float] = mapped_column(Float, nullable=False)
    shap_value: Mapped[float] = mapped_column(Float, nullable=False)

    prediction: Mapped[Prediction] = relationship(back_populates="shap_values")
