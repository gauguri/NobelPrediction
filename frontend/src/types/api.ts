export interface ShapAttribution {
  feature_name: string
  feature_value: number
  shap_value: number
}

export interface Prediction {
  candidate_id: number
  candidate_name: string
  affiliation: string
  field: string
  headshot_url?: string | null
  probability: number
  horizon: string
  year: number
  shap_values: ShapAttribution[]
  rank?: number
}

export interface CandidateDetail {
  candidate_id: number
  candidate_name: string
  affiliation: string
  country?: string | null
  headshot_url?: string | null
  field: string
  total_citations: number
  h_index: number
  recent_trend: number
  seminal_score: number
  award_count: number
}

export interface BacktestMetric {
  field: string
  hit_at_10: number
  auc_pr: number
  brier_score: number
  years_covered: [number, number]
}

export interface ProvenanceRecord {
  feature_name: string
  source: string
  as_of_date: string
  latency_days: number
}

export interface ProvenanceResponse {
  candidate_id: number
  records: ProvenanceRecord[]
}
