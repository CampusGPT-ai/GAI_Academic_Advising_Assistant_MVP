// A Memoized Component for Rendering Chat History
import { Box } from "@mui/material";
import React, { FC } from "react";
import "../../../../assets/styles.css";
import messageSample from "../../../../model/messages/messageSample.json";
import ParentMessage, { Message, MessageContent } from "../../../../model/messages/messages";
import ChatBotChat from "./chatBotChat";
import ChatUserChat from "./chatUserChat";

interface ChatHistoryProps {
  /** An array of messages to display in the chat. */
  messages: ParentMessage[];
  onFollowupClicked: (message: string) => void;
}

const ChatMessageHistory: FC<ChatHistoryProps> = React.memo(({ messages, onFollowupClicked }) => {
  return (
    <div>
      {messages.map((m, index) => {

        const pm: MessageContent[] = m.message.message
        console.log(`mapping pm:  ${JSON.stringify(pm)}`)

        return (
          <div key={index}>
            {
              pm.map((mc: MessageContent, index) => {
                console.log(`mapping messages for messageList : ${JSON.stringify(mc)}`)

                return (
                  <React.Fragment key={index}>
                    {mc.role === "bot" ? (
                      <ChatBotChat message={mc} follow_up_questions={m.follow_up_questions}
                        citations={m.citations}
                        onFollowupClicked={onFollowupClicked} />
                    ) : (
                      <ChatUserChat text={mc.message} />
                    )
                    }
                    <Box sx={{ height: "50px" }} />
                  </React.Fragment>

                )
              })}
          </div>
        )
      })
      }
    </div>
  )
});

export default ChatMessageHistory;