import React, { FC } from "react";
import { Typography, Box } from "@mui/material";
import "../../assets/styles.css";
interface ChatUserChatProps {
  text?: string;
}

const ChatUserChat: FC<ChatUserChatProps> = ({
  text
}) => {
  return (
    <div className="chatUserContainerAlign">
      <Box className="chatUserChatContainer">
          <Typography variant="body1">{text}</Typography>
      </Box>
    </div>
  );
};

ChatUserChat.defaultProps = {
  text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus.",
};

export default ChatUserChat;
