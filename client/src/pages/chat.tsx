import { Box, Grid } from "@mui/material";
import { FC } from "react";
import Conversation from "../model/conversation/conversations";
import Message from "../model/messages/messages";
import ChatActive from "../components/chat/chatActive";
import ChatHistoryContainer from "../components/chatHistory/chatHistory";

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
  sampleQuestions: string[];
  chatResponse?: Message;
  isLoading: boolean;
  isLoggedIn: boolean;
  sendChatClicked: (messageText: string) => void;
  setConversation: (conversation: Conversation) => void;
  newChat: () => void;
  error: string;
  isError: boolean;
  messageHistory: Message[];
  conversationTitle?: string;
  conversations: Conversation[];
  currentAnswerRef: React.MutableRefObject<any>;
}

const Chat: FC<ChatProps> = ({
  isLoading,
  isLoggedIn,
  sampleQuestions,
  chatResponse,
  sendChatClicked,
  messageHistory,
  conversations,
  setConversation,
  conversationTitle,
  newChat,
  error,
  isError, 
  currentAnswerRef
}) => {
  // conversations: Array<Conversation>;
  
  return (
 
      <Box height={"100%"} display="flex" justifyContent={"center"} width="100vw">
      <Grid container width="100%" m={10}>
        {isLoggedIn && (
          <Grid item xs={3}>
            <Box sx={{ m: "20px" }}>
              <ChatHistoryContainer //src/sections/chat/chatHistory
                isLoading={isLoading}
                setConversation={setConversation}
                newChat={newChat}
                conversations={conversations}
              />
            </Box>
          </Grid>
        )}
        <Grid item xs={isLoggedIn ? 9 : 12}>
          <ChatActive //src/sections/chat/chatActive
            isLoading={isLoading}
            chatResponse={chatResponse}
            messageHistory={messageHistory}
            sendChatClicked={sendChatClicked}
            error={error}
            isError={isError}
            sampleQuestions={sampleQuestions}
            convoTitle={conversationTitle}
            currentAnswerRef={currentAnswerRef}
          />
        </Grid>
      </Grid>
      </Box>
 
  );
};

Chat.defaultProps = {
  isLoggedIn: true,
  isLoading: false,
  sampleQuestions: ["question 1", "question 2", "question 3"],
};

export default Chat;
