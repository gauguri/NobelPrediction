import { Avatar, Chip, Paper, Table, TableBody, TableCell, TableHead, TableRow, Tooltip, Typography } from '@mui/material';
import { PredictionCandidate } from '../api/client';

interface Props {
  predictions: PredictionCandidate[];
  onSelect?: (prediction: PredictionCandidate) => void;
}

const formatProbability = (value: number) => `${(value * 100).toFixed(1)}%`;

const PredictionTable = ({ predictions, onSelect }: Props) => {
  return (
    <Paper elevation={2} sx={{ overflowX: 'auto' }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Rank</TableCell>
            <TableCell>Candidate</TableCell>
            <TableCell>Affiliation</TableCell>
            <TableCell>Probability</TableCell>
            <TableCell>Top Drivers</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {predictions.map((item, index) => (
            <TableRow
              key={item.candidate.id}
              hover
              sx={{ cursor: onSelect ? 'pointer' : 'default' }}
              onClick={() => onSelect?.(item)}
            >
              <TableCell>{index + 1}</TableCell>
              <TableCell>
                <Avatar
                  src={item.candidate.headshot_url || undefined}
                  alt={item.candidate.full_name}
                  sx={{ width: 32, height: 32, mr: 1, display: 'inline-flex', verticalAlign: 'middle' }}
                />
                <Typography component="span" sx={{ ml: 1 }}>
                  {item.candidate.full_name}
                </Typography>
                {item.candidate.clarivate_laureate && <Chip label="Clarivate" size="small" color="secondary" sx={{ ml: 1 }} />}
              </TableCell>
              <TableCell>{item.candidate.affiliation ?? '—'}</TableCell>
              <TableCell>{formatProbability(item.probability)}</TableCell>
              <TableCell>
                {Object.entries(item.top_features)
                  .slice(0, 3)
                  .map(([feature, value]) => (
                    <Tooltip key={feature} title={`SHAP: ${value.toFixed(3)}`}>
                      <Chip label={`${feature}`} size="small" sx={{ mr: 0.5 }} />
                    </Tooltip>
                  ))}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  );
};

export default PredictionTable;
