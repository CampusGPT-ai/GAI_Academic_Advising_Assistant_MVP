import { Box } from "@mui/material";
import React, { FC } from "react";
import "../../../assets/styles.css";
import messageSample from "../../../model/messages/messageSample.json";
import ParentMessage, { Citation, Followup, Message, Timestamp } from "../../../model/messages/messages";
import ChatBotChat from "./chatMessageElements/chatBotChat";
import ChatMessageHistory from "./chatMessageElements/chatMessageHistory";
import ChatUserChat from "./chatMessageElements/chatUserChat";
//for default props
const jsonString = JSON.stringify(messageSample);

/**
 * Props for the ChatMessages component.
 */
interface ChatMessagesProps {
  onFollowupClicked: (message: string) => void;
  /** Whether the component is currently loading. */
  isLoading?: boolean;
  userQuestion?: string;
  /** Whether an error occurred while loading the component. */
  isError?: boolean;
  /** the latest bot response to stream*/
  chatResponse?: string;
  follow_up_questions?: Followup[];
  citations?: Citation[];
  /** A function to call when the component should retry loading. */
  onRetry?: () => void;
  /** An error message to display if an error occurred while loading the component. */
  error?: string;
  /**An array of messages to display as history */
  messageHistory?: Array<ParentMessage>;

  currentAnswerRef: React.MutableRefObject<any>;
}

function getCurrentTimestamp(): Timestamp {
  return {
    $date: Date.now() // Current time in milliseconds
  };
}

const ChatMessages: FC<ChatMessagesProps> = ({
  chatResponse,
  userQuestion,
  follow_up_questions,
  citations,
  onFollowupClicked,
  isLoading,
  isError,
  onRetry,
  error,
  messageHistory, 
  currentAnswerRef
}) => {
  console.log(`passing loading and error states.  loading: ${isLoading} error: ${isError}`)
  const botMessage : Message = {role: 'assistant', message: chatResponse || "", created_at: getCurrentTimestamp() }
  return (
    <Box display="flex" flexGrow={1}>
      {messageHistory &&
      <ChatMessageHistory messages={messageHistory} onFollowupClicked={onFollowupClicked}/>}
      { isLoading && userQuestion && <ChatUserChat text={userQuestion}></ChatUserChat>}
      { chatResponse && 
        <ChatBotChat
            message={botMessage}
            follow_up_questions={follow_up_questions}
            citations={citations}
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


export default ChatMessages;
