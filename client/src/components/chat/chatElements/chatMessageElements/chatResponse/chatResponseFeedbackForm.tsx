import React, { useState } from 'react';
import { Box, TextField, Typography, Slider, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, FormControl, FormLabel } from '@mui/material';
import submitChatFeedback from '../../../../../api/sendFeedback';

interface ScaleQuestionProps {
  label: string;
  onScaleChange: (value: number | number[]) => void;
}

const ScaleQuestion: React.FC<ScaleQuestionProps> = ({ label, onScaleChange }) => {
  const marks = [
    { value: 1, label: '1' },
    { value: 2, label: '2' },
    { value: 3, label: '3' },
    { value: 4, label: '4' },
    { value: 5, label: '5' },
  ];

  return (
    <TableRow>
      <TableCell>{label}</TableCell>
      <TableCell align="center">
        <Slider
          defaultValue={3}
          step={1}
          marks={marks}
          min={1}
          max={5}
          valueLabelDisplay="auto"
          onChange={(event, value) => onScaleChange(value)}
        />
      </TableCell>
     
    </TableRow>
  );
};

const FeedbackForm: React.FC<{ onSubmit: (data: any) => void }> = ({ onSubmit }) => {
  const [responses, setResponses] = useState({
    relevance: { scale: 3},
    accuracy: { scale: 3},
    usefulness: { scale: 3},
    helpfulnessOfLinks: { scale: 3},
    learnMoreOptions: { scale: 3},
    comments : { comment: ''},
  });

  const handleScaleChange = (question: keyof typeof responses, value: number | number[]) => {
    setResponses(prev => ({ ...prev, [question]: { ...prev[question], scale: value } }));
  };

  const handleCommentChange = (comment: string) => {
    setResponses(prev => ({ ...prev, comments: { comment } }));
  };

  return (
    <Box width={800} p={2}>
      <Typography variant="h6" textAlign="center">Feedback Form</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width={'70%'}>Feedback</TableCell>
              <TableCell align="center">1 = low, 5 = high</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <ScaleQuestion
              label="Relevance: Did the AI seem to understand your question and provide a response that was directly related to your question?"
              onScaleChange={(value) => handleScaleChange('relevance', value)}
            />
            <ScaleQuestion
              label="Accuracy: Was the AI response accurate to the best of your knowledge (it didn’t create answers that were incorrect or untrue)?"
              onScaleChange={(value) => handleScaleChange('accuracy', value)}
            />
            <ScaleQuestion
              label="Usefulness: Did the AI response give you information that you would act on?"
              onScaleChange={(value) => handleScaleChange('usefulness', value)}
            />
            <ScaleQuestion
              label="Helpfulness of Links provided: In the response to your question, was the information provided in the links relevant?"
              onScaleChange={(value) => handleScaleChange('helpfulnessOfLinks', value)}
            />
            <ScaleQuestion
              label="“Learn More” Options: Were topics in the “Learn More” section related to the chat topic?"
              onScaleChange={(value) => handleScaleChange('learnMoreOptions', value)}
            />
            <TableRow>
             <TableCell>
        <TextField
          fullWidth
          label="Comments"
          variant="outlined"
          multiline
          rows={2}
          onChange={(e) => handleCommentChange(e.target.value)}
        />
      </TableCell>
      </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
      <Button
        fullWidth
        variant="contained"
        color="primary"
        onClick={onSubmit.bind(null, responses)}
        sx={{ mt: 2 }}
      >
        Submit
      </Button>
    </Box>
  );
};

export default FeedbackForm;
