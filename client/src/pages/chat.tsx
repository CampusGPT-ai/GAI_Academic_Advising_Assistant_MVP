import { Box, Grid } from "@mui/material";
import React, { FC } from "react";
import Conversation from "../model/conversation/conversations";
import ParentMessage, {Followup, Citation}  from "../model/messages/messages";
import ChatActive from "../components/chat/chatContainer";
import ChatHistory from "../components/chatHistory/chatHistoryList";

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
  chatResponse?: string;
  follow_up_questions?: Followup[];
  citations?: Citation[];
  isLoading: boolean;
  appStatus?: string;

  sendChatClicked: (messageText: string) => void;
  setConversation: (conversation: Conversation) => void;
  newChat: () => void;

  isError: boolean;
  messageHistory?: ParentMessage[];
  conversationTitle?: string;
  conversations: Conversation[];
  currentAnswerRef: React.MutableRefObject<any>;

  chatWidth: string;
}

const Chat: FC<ChatProps> = ({
  isLoading,
  appStatus,
  sampleQuestions,
  chatResponse,
  follow_up_questions,
  citations,
  sendChatClicked,
  messageHistory,
  conversationTitle,

  isError, 
  currentAnswerRef,

  chatWidth
}) => {
  console.log(`current app status is ${appStatus}`)
  console.log("loading chat page with ",JSON.stringify(ChatHistory))
  
  return (
 
      <Box height={"100%"} display="flex" justifyContent={"center"} width={chatWidth}>
          <ChatActive //src/sections/chat/chatActive
            isLoading={isLoading}
            chatResponse={chatResponse}
            follow_up_questions={follow_up_questions}
            citations={citations}
            messageHistory={messageHistory}
            sendChatClicked={sendChatClicked}

            isError={isError}
            sampleQuestions={sampleQuestions}
            convoTitle={conversationTitle}
            currentAnswerRef={currentAnswerRef}

          />
      </Box>
 
  );
};

Chat.defaultProps = {
  isLoading: false,
  sampleQuestions: ["question 1", "question 2", "question 3"],
};

export default Chat;
