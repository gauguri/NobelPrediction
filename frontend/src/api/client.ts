import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
});

export interface PredictionCandidate {
  candidate: {
    id: number;
    full_name: string;
    affiliation: string | null;
    headshot_url: string | null;
    clarivate_laureate: boolean;
  };
  prediction_year: number;
  horizon: 'one_year' | 'three_year';
  probability: number;
  top_features: Record<string, number>;
  shap_values: Record<string, number>;
  created_at: string;
}

export interface PredictionResponse {
  field: string;
  horizon: string;
  generated_at: string;
  predictions: PredictionCandidate[];
}

export interface BacktestMetric {
  field: string;
  metric: string;
  value: number;
  details: Record<string, unknown>;
}

export interface BacktestResponse {
  field: string;
  metrics: BacktestMetric[];
}

export const fetchPredictions = async (field: string, horizon: string) => {
  const { data } = await apiClient.get<PredictionResponse>(`/predictions/${field}`, {
    params: { horizon },
  });
  return data;
};

export const fetchBacktests = async (field: string) => {
  const { data } = await apiClient.get<BacktestResponse>(`/predictions/${field}/backtests`);
  return data;
};

