
import { Box, CircularProgress, Typography, useTheme } from "@mui/material";
import propTypes from "prop-types";
import React, { FC } from "react";
import messageSample from "../../../../model/messages/messageSample.json";
import { MessageContent, Citation} from "../../../../model/messages/messages";
import ChatBotChatResponse from "./chatResponse/chatBotChatResponse";

//for default props
const jsonString = JSON.stringify(messageSample);
//const sampleMessages = JSON.parse(jsonString) as Message[];
const sampleMessages = [] as MessageContent[];

interface ChatBotChatProps {
  isLoading?: boolean;
  isError?: boolean;
  message?: string;
  follow_up_questions?: string[];
  citations?: Citation[];
  onRetry?: () => void;
  onFollowupClicked: (message: string) => void;
  error?: string;
  currentAnswerRef?: React.MutableRefObject<any>;
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
  follow_up_questions,
  citations,
  isLoading,
  isError,
  onRetry,
  onFollowupClicked,
  error,
  currentAnswerRef
}) => {
  const theme = useTheme();
  //console.log(`checking message content on bot return: ${JSON.stringify(follow_up_questions)}`)
  return (
      
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        p: 1,
        width: '90%',
        minWidth: '600px',
        boxShadow: theme.shadows[2],
        backgroundColor: theme.palette.primary.contrastText,
      }}>
        {(!message || message === '') && (
          <div>
            <CircularProgress
              size={20}
              thickness={5}
              style={{ marginLeft: 10 }}
              aria-label="waiting for bot response"
            />
            <Typography variant="body1">Generating Answer</Typography>
          </div>
        )}

{
  /* isError && !isLoading && (
    <ChatBotChatError onRetry={onRetry} error={error} />
  ) */
}

        {!isError && message && (
          <ChatBotChatResponse message={message}
           follow_up_questions={follow_up_questions}
            citations={citations}
             currentAnswerRef={currentAnswerRef}
              onFollowupClicked={onFollowupClicked}/>)
      }
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
