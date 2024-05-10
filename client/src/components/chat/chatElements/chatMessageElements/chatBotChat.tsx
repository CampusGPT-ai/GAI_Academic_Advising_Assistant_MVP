
import { Box, CircularProgress, Typography, useTheme } from "@mui/material";
import propTypes from "prop-types";
import React, { FC, useEffect } from "react";
import messageSample from "../../../../model/messages/messageSample.json";
import { MessageContent, Citation} from "../../../../model/messages/messages";
import ChatBotChatResponse from "./chatResponse/chatBotChatResponse";
import ChatBotChatError from "./chatResponse/chatResponseElements/chatBotChatError";
import RateReviewIcon from '@mui/icons-material/RateReview';
import FeedbackForm from "./chatResponse/chatResponseFeedbackForm";
//for default props
const jsonString = JSON.stringify(messageSample);
//const sampleMessages = JSON.parse(jsonString) as Message[];
const sampleMessages = [] as MessageContent[];

interface ChatBotChatProps {
  isLoading?: boolean;
  isError?: boolean;
  message?: string;
  onRetry?: () => void;
  error?: string;
}

/**
 * A component that displays a chat message from a chatbot.
 * @param isLoading - Is the component in the loading state?
 * @param isError - Is the component in the error state?
 * @param message - The message to display.
 * @param onRetry - Callback to retry loading the message.
 * @param error - The error message to display.
 * @returns A React component that displays a chat message from a chatbot.
 */
const ChatBotChat: FC<ChatBotChatProps> = ({
  message,
  isLoading,
  isError,
  onRetry,
  error
}) => {
  const theme = useTheme();
  const [formatted_message, setFormattedMessage] = React.useState<string>('');
  const [showFeedback, setFeedback] = React.useState<boolean>(false);
  const [feedbackSent, setFeedbackSent] = React.useState<boolean>(false);
  function hyperlinkPreviousWord(text: string) {
    let cleanedText = text.replace(/\[\s*(Source|Links)?:?\s*\]|\(\s*(Source|Links)?:?\s*\)/gi, '');

    const urlRegex = /([^.?!]+\s?\b)\s\[(https?:\/\/\S+)\]/gi;
    let replacement = cleanedText.replace(urlRegex, (match, precedingSentence, url) => {
      // Replace the matched pattern with the preceding sentence wrapped in an anchor tag
      return `<a target="_blank" style="text-decoration: underline;" href="${url}">${precedingSentence}</a>`;
    });
    return replacement;
}
  useEffect(() => {
    message && setFormattedMessage(hyperlinkPreviousWord(message));
  },[message])


  return (
      
      <Box sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        p: 1,
        width: '90%',
        border: '1px solid #E0E0E0',
        minWidth: '600px',
        boxShadow: theme.shadows[2],
        backgroundColor: theme.palette.primary.contrastText,
      }}>

      {
        isError && !isLoading && (
          <ChatBotChatError onRetry={onRetry} error={error} />
        ) 
      }

        {!isError && message && (
          <ChatBotChatResponse message={formatted_message}
             />)
      }
<Box sx={{
        display: 'flex',
        alignItems: 'center',
        flexDirection: 'column',
        p: 1,
        width: '100%'
      }}>
        {feedbackSent && <Box sx={{ display: 'flex', alignItems: 'flex-end',flexDirection:'row', width: '100%' }}>
          <Typography variant="caption" sx={{ flexGrow: 1, textAlign: 'right' }}>Feedback Sent. Thank you!</Typography>
          </Box>}
        {!showFeedback && !feedbackSent && <Box sx={{ display: 'flex', alignItems: 'flex-end',flexDirection:'row', width: '100%' }}>
        <Typography variant="caption" sx={{ flexGrow: 1, textAlign: 'right' }}>Review Response&nbsp;&nbsp;</Typography>
        <RateReviewIcon onClick={() => setFeedback(true)} />
        </Box>}
        {showFeedback && !feedbackSent && (
          <FeedbackForm onSubmit={(data) => {
            setFeedback(false);
            setFeedbackSent(true);
          }} />
        )}
      </Box>
    </Box>
  );
};

ChatBotChat.propTypes = {
  /**
   * Is the component in the loading state?
   */
  isLoading: propTypes.bool,
  /**
   * Is the component in the error state?
   */
  isError: propTypes.bool,
  /**
   * The message to display
   */
  message: propTypes.any,
  /**
   * Callback to retry loading the message
   */
  onRetry: propTypes.func,
  /**
   * The error message to display
   */
  error: propTypes.string,

};
ChatBotChat.defaultProps = {
  isLoading: false,
  isError: false,
  error: "this is an error",
  message: "this is a message",
};

export default ChatBotChat;
