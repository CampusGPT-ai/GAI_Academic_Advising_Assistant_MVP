import React, { useState } from 'react';
import { Box, TextField, Typography, Slider, Button, FormControl, FormLabel } from '@mui/material';
import submitChatFeedback from '../../../../../api/sendFeedback';

interface ScaleQuestionProps {
  label: string;
  begin: string;
  end: string;
  onCommentChange: (comment: string) => void;
  onScaleChange: (value: number | number[]) => void;
}

const ScaleQuestion: React.FC<ScaleQuestionProps> = ({ label, begin, end, onCommentChange, onScaleChange }) => {
  const marks = [
    { value: 1, label: '1' },
    { value: 2, label: '2' },
    { value: 3, label: '3' },
    { value: 4, label: '4' },
    { value: 5, label: '5' },
  ];

  return (
    <FormControl fullWidth margin="normal">
      <FormLabel>{label}</FormLabel>
      <Typography component="div" sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="caption" mr={2}>{begin}</Typography>
        <Slider
          defaultValue={3}
          step={1}
          marks={marks}
          min={1}
          max={5}
          valueLabelDisplay="auto"
          onChange={(event, value) => onScaleChange(value)}
        />
        <Typography variant="caption" ml={2}>{end}</Typography>
      </Typography>
      <TextField
        fullWidth
        margin="normal"
        label="Comments"
        variant="outlined"
        multiline
        rows={2}
        onChange={(e) => onCommentChange(e.target.value)}
      />
    </FormControl>
  );
};


const FeedbackForm: React.FC<{ onSubmit: (data: any) => void }> = ({ onSubmit }) => {
  const [responses, setResponses] = useState({
    q1_usefullness: { scale: 3, comment: '' },
    q2_relevancy: { scale: 3, comment: '' },
    q3_accuracy: { scale: 3, comment: '' },
  });

  const handleScaleChange = (question: keyof typeof responses, value: number | number[]) => {
    setResponses(prev => ({ ...prev, [question]: { ...prev[question], scale: value } }));
  };

  const handleCommentChange = (question: keyof typeof responses, comment: string) => {
    setResponses(prev => ({ ...prev, [question]: { ...prev[question], comment: comment } }));
  };

  const handleSubmit = () => {
    submitChatFeedback({ feedback: responses });
    onSubmit(responses);
  };

  return (
    <Box width={500} p={2}>
      <Typography variant="h6" textAlign="center">Feedback Form</Typography>
      <ScaleQuestion
        label="Information Usefullness: How useful was the information provided?"
        begin='Not at all useful'
        end='Extremely useful'
        onScaleChange={(value) => handleScaleChange('q1_usefullness', value)}
        onCommentChange={(comment) => handleCommentChange('q1_usefullness', comment)}
      />
      <ScaleQuestion
        label="Information Relevancy: How well did the response interpret the intent of what you were asking and provide directly relevant information?"
        begin="The information provided was irrelevant to what I was asking"
        end="The information provided is relevant for what I was asking"
        onScaleChange={(value) => handleScaleChange('q2_relevancy', value)}
        onCommentChange={(comment) => handleCommentChange('q2_relevancy', comment)}
      />
      <ScaleQuestion
        label="Information Accuracy: How accurate was the information provided, to the best of your knowledge?"
        begin="There are obvious factual errors in the response"
        end="The information is accurate for what I was asking"
        onScaleChange={(value) => handleScaleChange('q3_accuracy', value)}
        onCommentChange={(comment) => handleCommentChange('q3_accuracy', comment)}
      />
      <Button
        fullWidth
        variant="contained"
        color="primary"
        onClick={handleSubmit}
        sx={{ mt: 2 }}
      >
        Submit
      </Button>
    </Box>
  );
};

export default FeedbackForm;
