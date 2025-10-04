import {
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import dayjs from 'dayjs'
import { CandidateDetail, ProvenanceRecord } from '../types/api'

interface Props {
  candidate: CandidateDetail | null
  provenance: ProvenanceRecord[]
  onClose: () => void
}

function ProvenanceDrawer({ candidate, provenance, onClose }: Props) {
  return (
    <Drawer anchor="right" open={Boolean(candidate)} onClose={onClose} sx={{ '& .MuiDrawer-paper': { width: 360 } }}>
      <Box sx={{ p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Candidate details</Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Stack>
        {candidate && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1">{candidate.candidate_name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {candidate.affiliation}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Citations: {candidate.total_citations.toLocaleString()} | h-index: {candidate.h_index}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Awards tracked: {candidate.award_count}
            </Typography>
          </Box>
        )}

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Data provenance
          </Typography>
          <List>
            {provenance.map((record) => (
              <ListItem key={`${record.feature_name}-${record.source}`} alignItems="flex-start">
                <ListItemText
                  primary={record.feature_name}
                  secondary={
                    <>
                      <Typography variant="body2" color="text.secondary">
                        Source: {record.source}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        As of: {dayjs(record.as_of_date).format('YYYY-MM-DD')} ({record.latency_days} day latency)
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
            {!provenance.length && (
              <Typography variant="body2" color="text.secondary">
                No provenance metadata available for this candidate yet.
              </Typography>
            )}
          </List>
        </Box>
      </Box>
    </Drawer>
  )
}

export default ProvenanceDrawer
