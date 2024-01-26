import QuestionAnswerOutlinedIcon from "@mui/icons-material/QuestionAnswerOutlined";
import { Button, Grid, useTheme } from "@mui/material";
import { FC, useState } from "react";
import conversationSample from "../../model/conversation/conversationSample.json";
import Conversation from "../../model/conversation/conversations";

const jsonString = JSON.stringify(conversationSample);
const conversations = JSON.parse(jsonString) as Conversation[];

/**
 * Props for the ChatHistory component.
 */
interface ChatHistoryProps {
  /**
   * An array of Conversation objects representing the chat history.
   */
  conversations: Array<Conversation>;
  /**
   * A boolean indicating whether the chat history is currently being loaded.
   */
  convoIsLoading: boolean;
  /**
   * A function to set the active conversation by its ID.
   * @param conversationId - The ID of the conversation to set as active.
   */
  setConversation: (Conversation: Conversation) => void;
}

const ChatHistory: FC<ChatHistoryProps> = ({
  conversations,
  convoIsLoading,
  setConversation,
}) => {
  const theme = useTheme();
  const [selectedConversation, setSelectedConversation] = useState<
    string | null
  >(null);

  /**
   * Handles the selection of a conversation and updates the state accordingly.
   * @param conversation - The conversation object that was selected.
   */
  function handleSelectConversation(conversation: Conversation) {
    setSelectedConversation(conversation._id);
    setConversation(conversation);
    console.log("Selected Conversation ID: ", conversation._id);
  }

  return (
    <Grid container direction={"column"} spacing={2} padding={2}>
      {conversations.length > 0 ? (
        conversations.map((conversation, index) => (
          <Grid item key={index}>
            <Button
              variant="text"
              sx={{
                color: theme.palette.text.primary,
                textAlign: "left",
                whiteSpace: "normal",
                textTransform: "none",
                backgroundColor:
                  selectedConversation === conversation._id
                    ? "rgba(0, 0, 0, 0.1)"
                    : undefined,
              }}
              onClick={() => handleSelectConversation(conversation)}
            >
              <QuestionAnswerOutlinedIcon sx={{ mr: 1 }} />
              <span color={theme.palette.text.primary}>
              {conversation.topic}
              </span>
            </Button>
          </Grid>
        ))
      ) : (
        <div>
          {convoIsLoading && <div>Loading...</div>}
          {!convoIsLoading && <div>No conversations available </div>}
        </div>
      )}
    </Grid>
  );
};

ChatHistory.defaultProps = {
  convoIsLoading: false,
  conversations: conversations,
};

export default ChatHistory;
