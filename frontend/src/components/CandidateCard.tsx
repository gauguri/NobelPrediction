import { Avatar, Box, Button, Card, CardActions, CardContent, LinearProgress, Stack, Typography } from '@mui/material'
import Plot from 'react-plotly.js'
import { Prediction } from '../types/api'

interface Props {
  prediction: Prediction
  onSelect: (candidateId: number) => void
}

function CandidateCard({ prediction, onSelect }: Props) {
  const shapFeatures = prediction.shap_values.slice(0, 4)

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar src={prediction.headshot_url ?? undefined} sx={{ width: 56, height: 56 }}>
              {prediction.candidate_name.slice(0, 2)}
            </Avatar>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                #{prediction.rank ?? '-'}
              </Typography>
              <Typography variant="h6">{prediction.candidate_name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {prediction.affiliation}
              </Typography>
            </Box>
          </Stack>

          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Probability
            </Typography>
            <LinearProgress variant="determinate" value={prediction.probability * 100} sx={{ height: 10, borderRadius: 5 }} />
            <Typography variant="subtitle1" sx={{ mt: 1 }}>
              {(prediction.probability * 100).toFixed(1)}%
            </Typography>
          </Box>

          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Top drivers (pseudo-SHAP)
            </Typography>
            <Plot
              data={[
                {
                  type: 'bar',
                  orientation: 'h',
                  x: shapFeatures.map((item) => item.shap_value),
                  y: shapFeatures.map((item) => item.feature_name),
                  marker: { color: '#0b3d91' }
                }
              ]}
              layout={{
                width: 300,
                height: 200,
                margin: { l: 100, r: 10, t: 10, b: 30 },
                xaxis: { title: 'Impact' }
              }}
              config={{ displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </Box>
        </Stack>
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => onSelect(prediction.candidate_id)}>
          View profile & provenance
        </Button>
      </CardActions>
    </Card>
  )
}

export default CandidateCard
