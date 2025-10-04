import axios from 'axios'
import { BacktestMetric, CandidateDetail, Prediction, ProvenanceResponse } from '../types/api'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api/v1'
})

export async function fetchShortlist(field: string, horizon: string): Promise<Prediction[]> {
  const response = await api.get<Prediction[]>(`/predictions/shortlist`, {
    params: { field, horizon }
  })
  return response.data
}

export async function fetchCandidateDetail(candidateId: number): Promise<CandidateDetail> {
  const response = await api.get<CandidateDetail>(`/predictions/candidates/${candidateId}`)
  return response.data
}

export async function fetchBacktests(field: string): Promise<BacktestMetric[]> {
  const response = await api.get<BacktestMetric[]>(`/predictions/backtests`, { params: { field } })
  return response.data
}

export async function fetchProvenance(candidateId: number): Promise<ProvenanceResponse> {
  const response = await api.get<ProvenanceResponse>(`/predictions/provenance/${candidateId}`)
  return response.data
}

export async function triggerEtl() {
  await api.post(`/training/etl`)
}

export async function triggerTraining() {
  await api.post(`/training/model`)
}
