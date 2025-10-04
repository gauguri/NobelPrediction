import Plot from 'react-plotly.js';
import { PredictionCandidate } from '../api/client';

interface Props {
  prediction: PredictionCandidate | null;
}

const FeatureImportanceChart = ({ prediction }: Props) => {
  if (!prediction) {
    return null;
  }

  const shapEntries = Object.entries(prediction.top_features);
  if (shapEntries.length === 0) {
    return null;
  }
  const features = shapEntries.map(([name]) => name);
  const values = shapEntries.map(([, value]) => value);

  return (
    <Plot
      data={[
        {
          type: 'bar',
          x: values,
          y: features,
          orientation: 'h',
          marker: { color: values.map((v) => (v > 0 ? '#1a237e' : '#ff6f00')) },
        },
      ]}
      layout={{
        title: `${prediction.candidate.full_name} – Top Feature Contributions`,
        height: Math.max(300, features.length * 40),
        margin: { l: 150, r: 30, t: 60, b: 40 },
      }}
      config={{ responsive: true, displayModeBar: false }}
    />
  );
};

export default FeatureImportanceChart;
