import { Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { BacktestResponse } from '../api/client';

interface Props {
  backtests: BacktestResponse | null;
}

const BacktestPanel = ({ backtests }: Props) => {
  if (!backtests) return null;

  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Backtest Metrics ({backtests.field.toUpperCase()})
      </Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Metric</TableCell>
            <TableCell>Value</TableCell>
            <TableCell>Details</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {backtests.metrics.map((metric) => (
            <TableRow key={metric.metric}>
              <TableCell>{metric.metric}</TableCell>
              <TableCell>{metric.value.toFixed(3)}</TableCell>
              <TableCell>{metric.details?.timeframe ?? '—'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  );
};

export default BacktestPanel;
