// A Memoized Component for Rendering Chat History
import { Box } from "@mui/material";
import React, { FC } from "react";
import "../../../assets/styles.css";
import messageSample from "../../../model/messages/messageSample.json";
import Message from "../../../model/messages/messages";
import ChatBotChat from "./chatMessage/chatBotChat";
import ChatUserChat from "./chatMessage/chatUserChat";

//for default props
const jsonString = JSON.stringify(messageSample);
const sampleMessages = JSON.parse(jsonString) as Message[];

interface ChatHistoryProps {
    /** An array of messages to display in the chat. */
    messages: Message[];
    onFollowupClicked: (message: string) => void;
}

const ChatMessageHistory: FC<ChatHistoryProps> = React.memo(({ messages, onFollowupClicked }) => {
    return (
    <>
    {messages.map((message, index) => (
      <React.Fragment key={index}>
        {message.role === "bot" ? (
          <ChatBotChat message={message} onFollowupClicked={onFollowupClicked}/>
        ) : (
          <ChatUserChat text={message.message} />
        )}
        <Box sx={{ height: "50px" }} />
      </React.Fragment>
    ))}
    </>
    )
  });

  export default ChatMessageHistory;