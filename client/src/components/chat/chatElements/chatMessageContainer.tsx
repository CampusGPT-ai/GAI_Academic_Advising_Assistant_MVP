import { Box, CircularProgress, Typography } from "@mui/material";
import React, { FC, useEffect, useRef, Component } from "react";
import "../../../assets/styles.css";
import messageSample from "../../../model/messages/messageSample.json";
import ParentMessage, { Citation, MessageContent, Timestamp } from "../../../model/messages/messages";
import ChatBotChat from "./chatMessageElements/chatBotChat";
import ChatMessageHistory from "./chatMessageElements/chatMessageHistory";
import ChatUserChat from "./chatMessageElements/chatUserChat";
import ChatFollowUp from "./chatMessageElements/chatResponse/chatResponseElements/chatFollowUp";
import { MessageSimple } from "../../../model/messages/messages";
import AppStatus from "../../../model/conversation/statusMessages";
import ChatBotChatError from "./chatMessageElements/chatResponse/chatResponseElements/chatBotChatError";
import { useTheme } from "@emotion/react";
import { Outcomes } from "../../../api/fetchOutcomes";
import { Apps } from "@mui/icons-material";
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
  isError?: boolean;
  currentAnswerRef: React.MutableRefObject<any>;
  opportunities?: Outcomes[];

  /** A function to call when the component should retry loading. */
  onRetry?: () => void;
  onFollowUpClicked: (text: string) => void;

  /**An array of messages to display as history */
  messageHistory?: MessageSimple[];

}

function getCurrentTimestamp(): Timestamp {
  const theme = useTheme();
  return {
    $date: Date.now() // Current time in milliseconds
  };
}

const ChatMessages: FC<ChatMessagesProps> = ({
  appStatus,
  errMessage,
  onRetry,
  isError,
  messageHistory, 
  opportunities,
  onFollowUpClicked,
  
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" }  )
  });

  // console.log(`testing app status: ${appStatus}`)
  return (
    <Box display="flex" flexDirection={'column'} sx={{
    height: "90%",
    overflowY: "auto",
    }}>
      {messageHistory && appStatus !== AppStatus.GettingMessageHistory &&
      <ChatMessageHistory messages={messageHistory} isLoading={appStatus===AppStatus.GeneratingChatResponse} isError={isError} onRetry={onRetry}/>}
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        flexDirection: 'column',
        alignItems: 'center',
        justifyItems: 'center',
      }}>
        {(appStatus === AppStatus.GeneratingChatResponse || appStatus === AppStatus.GettingMessageHistory) && <CircularProgress />}
        {appStatus === AppStatus.GeneratingChatResponse &&
          <Typography variant="body1" color="textSecondary" align="center"> 
            Generating response...
          </Typography>}
        {appStatus === AppStatus.Error && <ChatBotChatError onRetry={onRetry} error={errMessage} />}
      </Box>
      {opportunities && appStatus === AppStatus.Idle &&
        <Box ref={scrollRef} width='100%'>
        <Typography variant="body1">Learn More About: </Typography>
        {
          opportunities && opportunities.map((opportunity, index) => {
            return (
              <Box key={index} p={1}>
                <ChatFollowUp text={opportunity} onFollowUpClicked={onFollowUpClicked} />
              </Box>
            )
          })
        }

      </Box>
      }
     

  
    </Box>
  );
};


export default ChatMessages;
