import React, { FC } from 'react';
import { Button } from "@mui/material";

/**
 * Props for the ChatSampleQuestions component.
 */
interface ChatSampleQuestionsProps {
  /**
   * The text to display on the button.
   */
  text: string;
  /**
   * Whether the component is currently loading.
   */
  isLoading: boolean;
  /**
   * Callback function to be called when the button is clicked.
   * @param text - The text to be passed to the callback function.
   */
  onSampleQuestionsClicked: (text: string) => void;
}

const ChatSampleQuestion: FC<ChatSampleQuestionsProps> = ({ text, isLoading, onSampleQuestionsClicked }) => {
  
  const handleQuestionClick = () => {
    if (!isLoading) {
      onSampleQuestionsClicked(text);
    }
  };

  return (
    <Button 
      variant="contained" 
      sx={{ margin: "10px" }} 
      onClick={handleQuestionClick} 
      disabled={isLoading} // Button is disabled when isLoading is true
    >
      {text}
    </Button>
  );
};

export default ChatSampleQuestion;
