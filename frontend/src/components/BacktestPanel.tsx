import { Card, CardContent, CardHeader, Typography } from '@mui/material'
import Plot from 'react-plotly.js'
import { BacktestMetric } from '../types/api'

interface Props {
  metrics: BacktestMetric[]
}

function BacktestPanel({ metrics }: Props) {
  if (!metrics.length) {
    return null
  }

  const metric = metrics[0]

  return (
    <Card variant="outlined">
      <CardHeader title="Backtest performance" subheader={`${metric.years_covered[0]} - ${metric.years_covered[1]}`} />
      <CardContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Historical hit rate and calibration for the Physics shortlist.
        </Typography>
        <Plot
          data={[
            {
              x: ['Hit@10', 'AUC-PR', 'Brier score'],
              y: [metric.hit_at_10, metric.auc_pr, metric.brier_score],
              type: 'bar',
              marker: { color: ['#0b3d91', '#f7a400', '#9c27b0'] }
            }
          ]}
          layout={{
            height: 300,
            margin: { l: 40, r: 20, t: 20, b: 40 },
            yaxis: { range: [0, 1] }
          }}
          config={{ displayModeBar: false }}
          style={{ width: '100%' }}
        />
      </CardContent>
    </Card>
  )
}

export default BacktestPanel
