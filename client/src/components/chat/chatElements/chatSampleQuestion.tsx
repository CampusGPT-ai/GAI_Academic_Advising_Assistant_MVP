import React, { FC } from 'react';
import { Button, Typography, Box, useTheme } from "@mui/material";
import TipsAndUpdatesOutlinedIcon from '@mui/icons-material/TipsAndUpdatesOutlined';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';
import AppStatus from '../../../model/conversation/statusMessages';
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
  appStatus: AppStatus;
  /**
   * Callback function to be called when the button is clicked.
   * @param text - The text to be passed to the callback function.
   */
  onSampleQuestionsClicked: (text: string) => void;
}

const ChatSampleQuestion: FC<ChatSampleQuestionsProps> = ({ text, appStatus, onSampleQuestionsClicked }) => {
  const theme = useTheme();
  const handleQuestionClick = () => {
    if (appStatus===AppStatus.Idle) {
      // console.log(`sample question clicked: ${text}`);
      onSampleQuestionsClicked(text);
    }
  };

  return (
    
    <Button 
      variant="outlined"
      sx={{ margin: "10px",
            width: "100%",
          display: "flex",
          justifyContent: "space-between",
          backgroundColor: theme.palette.primary.light,
          textTransform: "none",
          
        }} 
      onClick={handleQuestionClick} 
      disabled={appStatus!==AppStatus.Idle} // Button is disabled when isLoading is true
      startIcon={<TipsAndUpdatesOutlinedIcon />}
      endIcon={<ArrowRightAltIcon />}
    >
      
      <Typography variant="body1" p={1} textAlign={"left"}>{text}</Typography>
      
    </Button>
   
  );
};

export default ChatSampleQuestion;
