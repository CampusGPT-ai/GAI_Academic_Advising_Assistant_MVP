import { Box, CircularProgress, Typography } from "@mui/material";
import React, { FC } from "react";
import "../../../assets/styles.css";
import messageSample from "../../../model/messages/messageSample.json";
import ParentMessage, { Citation, MessageContent, Timestamp } from "../../../model/messages/messages";
import ChatBotChat from "./chatMessageElements/chatBotChat";
import ChatMessageHistory from "./chatMessageElements/chatMessageHistory";
import ChatUserChat from "./chatMessageElements/chatUserChat";
import { MessageSimple } from "../../../model/messages/messages";
import AppStatus from "../../../model/conversation/statusMessages";
import ChatBotChatError from "./chatMessageElements/chatResponse/chatResponseElements/chatBotChatError";
//for default props
const jsonString = JSON.stringify(messageSample);
const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';
/**
 * Props for the ChatMessages component.
 */
interface ChatMessagesProps {

  /** Whether the component is currently loading. */
  isLoading?: boolean;
  userQuestion?: string;
  appStatus: AppStatus;
  errMessage?: string;
  notifications?: string;
  /** the latest bot response to stream*/
  chatResponse?: string;
  currentAnswerRef: React.MutableRefObject<any>;

  /** A function to call when the component should retry loading. */
  onRetry?: () => void;

  /**An array of messages to display as history */
  messageHistory?: MessageSimple[];

}

function getCurrentTimestamp(): Timestamp {
  return {
    $date: Date.now() // Current time in milliseconds
  };
}

const ChatMessages: FC<ChatMessagesProps> = ({
  appStatus,
  errMessage,
  notifications,
  onRetry,
  messageHistory, 
  currentAnswerRef,
}) => {

  //console.log(`testing chat bot chat response ${chatResponse}`)
  return (
    <Box display="flex" flexDirection={'column'}>
      {messageHistory &&
      <ChatMessageHistory messages={messageHistory} />}
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        flexDirection: 'column',
        marginTop: '20px',
        marginBottom: '20px'
      }}>
        {appStatus === AppStatus.GeneratingChatResponse && <CircularProgress />}
        {appStatus === AppStatus.GeneratingChatResponse &&
          <Typography variant="body1" color="textSecondary" align="center"> 
            {notifications ? notifications : "Generating response..."}
          </Typography>}
        {appStatus === AppStatus.Error && <ChatBotChatError onRetry={onRetry} error={errMessage} />}
      </Box>
     

  
    </Box>
  );
};


export default ChatMessages;
