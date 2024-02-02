// A Memoized Component for Rendering Chat History
import { Box } from "@mui/material";
import React, { FC } from "react";
import "../../../../assets/styles.css";
import messageSample from "../../../../model/messages/messageSample.json";
import ParentMessage, {} from "../../../../model/messages/messages";
import ChatBotChat from "./chatBotChat";
import ChatUserChat from "./chatUserChat";

interface ChatHistoryProps {
    /** An array of messages to display in the chat. */
    messages: ParentMessage[];
    onFollowupClicked: (message: string) => void;
}

const ChatMessageHistory: FC<ChatHistoryProps> = React.memo(({ messages, onFollowupClicked }) => {
    return (
    <>
    {messages.map((message, index) => (
      message.messages.map((m, index) => (
        <React.Fragment key={index}>
          {m.role === "bot" ? (
          <ChatBotChat message={m} follow_up_questions={message.follow_up_questions}
           citations={message.citations}
            onFollowupClicked={onFollowupClicked}/>
          ) : (
          <ChatUserChat text={m.message} />
          )
          }
        <Box sx={{ height: "50px" }} />
      </React.Fragment>
      ))
      
    ))}
    </>
    )
  });

  export default ChatMessageHistory;