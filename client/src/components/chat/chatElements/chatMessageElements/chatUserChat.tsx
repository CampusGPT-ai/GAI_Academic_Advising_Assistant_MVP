import React, { FC } from "react";
import { Typography, Box, useTheme } from "@mui/material";
import "../../../../assets/styles.css";
interface ChatUserChatProps {
  text?: string;
}

const ChatUserChat: FC<ChatUserChatProps> = ({
  text
}) => {
  const theme = useTheme();
  return (
    <div className="chatUserContainerAlign">
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        p: 1,
        width: '90%',
        minWidth: '600px',
        boxShadow: theme.shadows[2],
        backgroundColor: theme.palette.secondary.light,
      }}>
          <Typography variant="body1">{text}</Typography>
      </Box>
    </div>
  );
};

ChatUserChat.defaultProps = {
  text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus.",
};

export default ChatUserChat;
