import { Container, Grid, Typography } from '@mui/material';
import { Route, Routes } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import CandidatePage from './pages/CandidatePage';

function App() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Typography variant="h3" fontWeight="bold">
            Nobel Prize Prediction Platform
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Transparent, data-driven forecasts with explainability and backtesting insights.
          </Typography>
        </Grid>
      </Grid>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/candidate/:id" element={<CandidatePage />} />
      </Routes>
    </Container>
  );
}

export default App;
