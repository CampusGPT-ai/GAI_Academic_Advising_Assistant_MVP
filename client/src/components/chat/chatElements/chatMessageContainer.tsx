import { Box } from "@mui/material";
import React, { FC } from "react";
import "../../../assets/styles.css";
import messageSample from "../../../model/messages/messageSample.json";
import ParentMessage, { Citation, MessageContent, Timestamp } from "../../../model/messages/messages";
import ChatBotChat from "./chatMessageElements/chatBotChat";
import ChatMessageHistory from "./chatMessageElements/chatMessageHistory";
import ChatUserChat from "./chatMessageElements/chatUserChat";
import { MessageSimple } from "../../../model/messages/messages";
import AppStatus from "../../../model/conversation/statusMessages";
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
  appStatus: AppStatus;

  /** the latest bot response to stream*/
  chatResponse?: string;
  follow_up_questions?: string[];
  citations?: Citation[];
  /** A function to call when the component should retry loading. */
  onRetry?: () => void;

  /**An array of messages to display as history */
  messageHistory?: MessageSimple[];

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
  appStatus,
  onFollowupClicked,
  isLoading,
  onRetry,
  messageHistory, 
  currentAnswerRef
}) => {

  //console.log(`testing chat bot chat response ${chatResponse}`)
  return (
    <Box display="flex" flexDirection={'column'}>
      {messageHistory &&
      <ChatMessageHistory messages={messageHistory} onFollowupClicked={onFollowupClicked}/>}
      {/**if the response is still generating, show the active question and response.  After response is done generating, it should be refreshed in the history */}
      { appStatus===AppStatus.GeneratingChatResponse && <ChatUserChat text={userQuestion}></ChatUserChat>}

      { appStatus===AppStatus.GeneratingChatResponse && 
      <Box><Box sx={{ height: "50px" }} />
        <ChatBotChat
            message={chatResponse}
            follow_up_questions={follow_up_questions}
            citations={citations}
            isLoading={isLoading}
            onFollowupClicked={onFollowupClicked}
            onRetry={onRetry}
            currentAnswerRef={currentAnswerRef}
          />
          </Box>}
    </Box>
  );
};


export default ChatMessages;
