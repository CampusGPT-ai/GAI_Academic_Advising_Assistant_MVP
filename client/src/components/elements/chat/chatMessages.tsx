import { Box } from "@mui/material";
import { FC } from "react";
import "../../../assets/styles.css";
import messageSample from "../../../model/messages/messageSample.json";
import Message from "../../../model/messages/messages";
import ChatBotChat from "./chatBot/chatBotChat";
import ChatMessageHistory from "./chatMessageHistory";

//for default props
const jsonString = JSON.stringify(messageSample);
const sampleMessages = JSON.parse(jsonString) as Message[];

/**
 * Props for the ChatMessages component.
 */
interface ChatMessagesProps {
  onFollowupClicked: (message: string) => void;
  /** Whether the component is currently loading. */
  isLoading?: boolean;
  /** Whether an error occurred while loading the component. */
  isError?: boolean;
  /** the latest bot response to stream*/
  chatResponse?: Message;
  /** A function to call when the component should retry loading. */
  onRetry?: () => void;
  /** An error message to display if an error occurred while loading the component. */
  error?: string;
  /**An array of messages to display as history */
  messageHistory?: Array<Message>;

  currentAnswerRef: React.MutableRefObject<any>;
}

const ChatMessages: FC<ChatMessagesProps> = ({
  chatResponse,
  onFollowupClicked,
  isLoading,
  isError,
  onRetry,
  error,
  messageHistory, 
  currentAnswerRef
}) => {
  console.log(`passing loading and error states.  loading: ${isLoading} error: ${isError}`)

  return (
    <Box>
      {messageHistory &&
      <ChatMessageHistory messages={messageHistory} onFollowupClicked={onFollowupClicked}/>}
      { chatResponse && 
        <ChatBotChat
            message={chatResponse}
            isLoading={isLoading}
            onFollowupClicked={onFollowupClicked}
            isError={isError}
            onRetry={onRetry}
            error={error}
            currentAnswerRef={currentAnswerRef}
          />}
    </Box>
  );
};

ChatMessages.defaultProps = {
  messageHistory: sampleMessages,
};

export default ChatMessages;
