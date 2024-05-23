import { Box, Grid } from "@mui/material";
import React, { FC } from "react";
import Conversation from "../model/conversation/conversations";
import ParentMessage, { Citation, MessageSimple}  from "../model/messages/messages";
import ChatActive from "../components/chat/chatContainer";
import AppStatus from "../model/conversation/statusMessages";
import { Outcomes } from "../api/fetchOutcomes"
/**
 * Props for the Chat component.
 * @interface
 * @property {string[]} sampleQuestions - An array of sample questions to display in the chat.
 * @property {boolean} isLoading - A boolean indicating whether the chat is currently loading.
 * @property {boolean} isLoggedIn - A boolean indicating whether the user is currently logged in.
 * @property {(messageText: string) => void} sendChatClicked - A function to handle when the user clicks the send button.
 * @property {() => void} setConversation - A function to set the current conversation.
 * @property {() => void} newChat - A function to start a new chat.
 * @property {string} error - A string containing the error message, if any.
 * @property {boolean} isError - A boolean indicating whether there is an error.
 * @property {Message[]} messageHistory - An array of messageHistory in the current conversation.
 * @property {string} [conversationTitle] - An optional string containing the title of the current conversation.
 * @property {Conversation[]} conversations - An array of all available conversations.
 */
interface ChatProps {
  sampleQuestions?: string[];
  isError: boolean;
  chatResponse?: string;
  appStatus: AppStatus;
  errMessage?: string;
  notifications?: string;
  sendChatClicked: (messageText: string) => void;
  messageHistory?: MessageSimple[];
  currentAnswerRef: React.MutableRefObject<any>;
  chatWidth: string;
  opportunities?: Outcomes[];
  currentUserQuestion?: string;
}

const Chat: FC<ChatProps> = ({
  appStatus,
  isError,
  sampleQuestions,
  sendChatClicked,
  messageHistory,
  currentAnswerRef,
  chatWidth,
  opportunities,
  currentUserQuestion,
}) => {
  //console.log(`current app status is ${appStatus}`)
  //console.log("loading chat page with ",JSON.stringify(messageHistory))
  const handleChatSend = (messageText: string) => {
    console.log(`Chat message sent: ${messageText}`)
    sendChatClicked(messageText);
  }
  
  return (




      <Box height={"100%"} display="flex" justifyContent={"center"} width={chatWidth}>
          <ChatActive //src/sections/chat/chatActive
            messageHistory={messageHistory}
            sendChatClicked={handleChatSend}
            appStatus={appStatus}
            sampleQuestions={sampleQuestions}
            isError={isError}
            currentAnswerRef={currentAnswerRef}
            opportunities={opportunities}
            currentUserQuestion={currentUserQuestion}
          />
      </Box>
 
  );
};

export default Chat;
