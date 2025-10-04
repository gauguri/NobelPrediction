import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, Button, ButtonGroup, CircularProgress, Grid, MenuItem, Select, Stack, Typography } from '@mui/material';
import PredictionTable from '../components/PredictionTable';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import BacktestPanel from '../components/BacktestPanel';
import { BacktestResponse, PredictionCandidate, PredictionResponse, fetchBacktests, fetchPredictions } from '../api/client';

const fields = [
  { value: 'physics', label: 'Physics' },
  { value: 'chemistry', label: 'Chemistry' },
  { value: 'medicine', label: 'Physiology/Medicine' },
  { value: 'economics', label: 'Economics' },
];

const horizons = [
  { value: 'one_year', label: 'This Year' },
  { value: 'three_year', label: 'Next 3 Years' },
];

const DashboardPage = () => {
  const [field, setField] = useState('physics');
  const [horizon, setHorizon] = useState('one_year');
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [backtests, setBacktests] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const selectedCandidate = useMemo<PredictionCandidate | null>(() => {
    if (!data || data.predictions.length === 0) return null;
    return data.predictions[0];
  }, [data]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [predictions, backtestData] = await Promise.all([
        fetchPredictions(field, horizon),
        fetchBacktests(field),
      ]);
      setData(predictions);
      setBacktests(backtestData);
    } catch (_error) {
      setError('Unable to load predictions. Ensure the backend is seeded.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [field, horizon]);

  return (
    <Stack spacing={3}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={4}>
          <Typography variant="h5">Shortlist Explorer</Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Select fullWidth value={field} onChange={(event) => setField(event.target.value)}>
            {fields.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.label}
              </MenuItem>
            ))}
          </Select>
        </Grid>
        <Grid item xs={12} md={4}>
          <ButtonGroup fullWidth>
            {horizons.map((item) => (
              <Button
                key={item.value}
                variant={horizon === item.value ? 'contained' : 'outlined'}
                onClick={() => setHorizon(item.value)}
              >
                {item.label}
              </Button>
            ))}
          </ButtonGroup>
        </Grid>
      </Grid>

      {error && <Alert severity="error">{error}</Alert>}
      {loading && <CircularProgress />} 

      {!loading && data && (
        <>
          <Typography variant="subtitle2" color="text.secondary">
            Generated at {new Date(data.generated_at).toLocaleString()}
          </Typography>
          <PredictionTable
            predictions={data.predictions}
            onSelect={(prediction) =>
              navigate(`/candidate/${prediction.candidate.id}`, {
                state: {
                  name: prediction.candidate.full_name,
                  affiliation: prediction.candidate.affiliation,
                  probability: prediction.probability,
                  features: prediction.top_features,
                },
              })
            }
          />
          <FeatureImportanceChart prediction={selectedCandidate} />
        </>
      )}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        <Button
          variant="outlined"
          href={`http://localhost:8000/reports/csv/${field}?horizon=${horizon}`}
          target="_blank"
        >
          Download CSV
        </Button>
        <Button
          variant="outlined"
          href={`http://localhost:8000/reports/pdf/${field}?horizon=${horizon}`}
          target="_blank"
        >
          Download PDF
        </Button>
      </Stack>

      <BacktestPanel backtests={backtests} />
    </Stack>
  );
};

export default DashboardPage;
