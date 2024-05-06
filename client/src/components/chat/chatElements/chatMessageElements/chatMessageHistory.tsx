// A Memoized Component for Rendering Chat History
import { Box } from "@mui/material";
import React, { FC } from "react";
import "../../../../assets/styles.css";
import messageSample from "../../../../model/messages/messageSample.json";
import ParentMessage, { Message, MessageContent, MessageSimple } from "../../../../model/messages/messages";
import ChatBotChat from "./chatBotChat";
import ChatUserChat from "./chatUserChat";

interface ChatHistoryProps {
  /** An array of messages to display in the chat. */
  messages: MessageSimple[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}


const ChatMessageHistory: FC<ChatHistoryProps> = React.memo(({ 
  messages,
  isLoading,
  isError,
  onRetry
}) => {
  //console.log(`chat message history set to: ${JSON.stringify(messages)}`)

  return (
    <Box>
      {messages.map((m, index) => {
        return (
          <React.Fragment key={index}>

            {m.role === "user" && (
              <>
                <ChatUserChat text={m.message} />
                <Box sx={{ height: "20px" }} />
              </>
            )
            }


            {m.role === "system" && (
              <>
                <ChatBotChat message={m.message} isLoading={isLoading} onRetry={onRetry} isError={isError} />
                <Box sx={{ height: "20px" }} />
              </>
            )
            }

          </React.Fragment>
        )
      })}
    </Box>
  )
})

export default ChatMessageHistory;