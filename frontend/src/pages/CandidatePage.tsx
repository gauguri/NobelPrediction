import { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button, Paper, Stack, Typography } from '@mui/material';

const CandidatePage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const state = location.state as {
    name?: string;
    affiliation?: string;
    probability?: number;
    features?: Record<string, number>;
  } | null;

  const featureEntries = useMemo(() => {
    if (!state?.features) return [];
    return Object.entries(state.features).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  }, [state]);

  return (
    <Stack spacing={2}>
      <Button variant="outlined" onClick={() => navigate(-1)}>
        Back
      </Button>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          {state?.name ?? 'Candidate'}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          {state?.affiliation ?? 'Affiliation unknown'}
        </Typography>
        <Typography variant="h6" sx={{ mt: 2 }}>
          Probability this cycle: {state?.probability ? `${(state.probability * 100).toFixed(1)}%` : 'N/A'}
        </Typography>
        <Typography variant="subtitle2" sx={{ mt: 3 }}>
          Key Drivers
        </Typography>
        <Stack spacing={1} sx={{ mt: 1 }}>
          {featureEntries.map(([feature, value]) => (
            <Typography key={feature}>
              <strong>{feature}</strong>: {value.toFixed(3)}
            </Typography>
          ))}
        </Stack>
      </Paper>
    </Stack>
  );
};

export default CandidatePage;
