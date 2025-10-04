import { Box, Container, Grid, MenuItem, Paper, Select, SelectChangeEvent, Stack, Tab, Tabs, Typography } from '@mui/material'
import { useEffect, useMemo, useState } from 'react'
import { fetchBacktests, fetchCandidateDetail, fetchProvenance, fetchShortlist } from './api/client'
import { BacktestMetric, CandidateDetail, Prediction, ProvenanceRecord } from './types/api'
import CandidateCard from './components/CandidateCard'
import BacktestPanel from './components/BacktestPanel'
import ProvenanceDrawer from './components/ProvenanceDrawer'

const fields = ['Physics']
const horizons = [
  { label: 'This year', value: 'one_year' },
  { label: '3-year horizon', value: 'three_year' }
]

function App() {
  const [field, setField] = useState('Physics')
  const [horizon, setHorizon] = useState('one_year')
  const [shortlist, setShortlist] = useState<Prediction[]>([])
  const [backtests, setBacktests] = useState<BacktestMetric[]>([])
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateDetail | null>(null)
  const [provenance, setProvenance] = useState<ProvenanceRecord[]>([])

  useEffect(() => {
    fetchShortlist(field, horizon).then(setShortlist)
  }, [field, horizon])

  useEffect(() => {
    fetchBacktests(field).then(setBacktests)
  }, [field])

  const shortlistWithRank = useMemo(
    () =>
      shortlist.map((prediction, index) => ({
        ...prediction,
        rank: index + 1
      })),
    [shortlist]
  )

  const handleCandidateSelect = async (candidateId: number) => {
    const detail = await fetchCandidateDetail(candidateId)
    setSelectedCandidate(detail)
    const provenanceResponse = await fetchProvenance(candidateId)
    setProvenance(provenanceResponse.records)
  }

  const handleFieldChange = (event: SelectChangeEvent<string>) => {
    setField(event.target.value)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack spacing={4}>
        <Box>
          <Typography variant="h3" gutterBottom>
            Nobel Prize Prediction Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Transparent shortlists combining bibliometrics, award trajectories, and topic momentum.
          </Typography>
        </Box>

        <Paper sx={{ p: 3 }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center" justifyContent="space-between">
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="h6">Field</Typography>
              <Select value={field} onChange={handleFieldChange} size="small">
                {fields.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
            </Stack>
            <Tabs value={horizon} onChange={(_, value) => setHorizon(value)} textColor="primary" indicatorColor="primary">
              {horizons.map((option) => (
                <Tab key={option.value} value={option.value} label={option.label} />
              ))}
            </Tabs>
          </Stack>
        </Paper>

        <Grid container spacing={3}>
          {shortlistWithRank.map((prediction) => (
            <Grid key={prediction.candidate_id} item xs={12} md={6} lg={4}>
              <CandidateCard prediction={prediction} onSelect={handleCandidateSelect} />
            </Grid>
          ))}
        </Grid>

        <BacktestPanel metrics={backtests} />
      </Stack>

      <ProvenanceDrawer
        candidate={selectedCandidate}
        provenance={provenance}
        onClose={() => setSelectedCandidate(null)}
      />
    </Container>
  )
}

export default App
