import { render, screen } from '@testing-library/react';
import PredictionTable from '../PredictionTable';
import { PredictionCandidate } from '../../api/client';

describe('PredictionTable', () => {
  const predictions: PredictionCandidate[] = [
    {
      candidate: {
        id: 1,
        full_name: 'Test Scientist',
        affiliation: 'Institute',
        headshot_url: null,
        clarivate_laureate: true,
      },
      prediction_year: 2024,
      horizon: 'one_year',
      probability: 0.42,
      top_features: {
        total_citations: 0.2,
        h_index: 0.1,
      },
      shap_values: {},
      created_at: new Date().toISOString(),
    },
  ];

  it('renders candidate name and probability', () => {
    render(<PredictionTable predictions={predictions} />);
    expect(screen.getByText('Test Scientist')).toBeInTheDocument();
    expect(screen.getByText('42.0%')).toBeInTheDocument();
  });
});
