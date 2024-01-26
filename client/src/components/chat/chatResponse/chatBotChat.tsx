
import { Box, CircularProgress, Typography } from "@mui/material";
import propTypes from "prop-types";
import React, { FC } from "react";
import "../../../assets/styles.css";
import messageSample from "../../../model/messages/messageSample.json";
import Message from "../../../model/messages/messages";
import ChatBotChatResponse from "./chatBotChatResponse";

//for default props
const jsonString = JSON.stringify(messageSample);
//const sampleMessages = JSON.parse(jsonString) as Message[];
const sampleMessages = [] as Message[];

interface ChatBotChatProps {
  isLoading?: boolean;
  isError?: boolean;
  message?: Message;
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
  isLoading,
  isError,
  onRetry,
  onFollowupClicked,
  error,
  currentAnswerRef
}) => {
  console.log(`is loading? ${isLoading}`)
  return (
      
      <Box className="chatBotChatContainer">
        {isLoading && (
          <div>
            <CircularProgress
              size={20}
              thickness={5}
              style={{ marginLeft: 10 }}
            />
            <Typography variant="body1">Generating Answer</Typography>
          </div>
        )}

{
  /* isError && !isLoading && (
    <ChatBotChatError onRetry={onRetry} error={error} />
  ) */
}

        {
        !isLoading && !isError && (
          <ChatBotChatResponse message={message} currentAnswerRef={currentAnswerRef} onFollowupClicked={onFollowupClicked}/>)
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
  message: sampleMessages[1],
};

export default ChatBotChat;
