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
  onFollowupClicked: (message: string) => void;
}

const ChatMessageHistory: FC<ChatHistoryProps> = React.memo(({ messages, onFollowupClicked }) => {
  return (
    <div>
      main loop from messages has {messages.length} message items. 
      {messages.map((m, index) => {
        return (
          <React.Fragment key={index}>

            {m.role === "user" && (
              <>
                <ChatUserChat text={m.message} />
                <Box sx={{ height: "50px" }} />
              </>
            )
            }


            {m.role === "assistant" && (
              <>
                <ChatBotChat message={m.message}
                  follow_up_questions={m.follow_up_questions}
                  citations={m.citations}
                  onFollowupClicked={onFollowupClicked} />
                <Box sx={{ height: "50px" }} />
              </>
            )
            }

          </React.Fragment>
        )
      })}
    </div>)
})

export default ChatMessageHistory;