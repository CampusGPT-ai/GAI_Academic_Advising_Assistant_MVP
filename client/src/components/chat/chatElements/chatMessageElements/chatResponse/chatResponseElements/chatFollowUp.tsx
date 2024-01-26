import { Button, useTheme } from "@mui/material";
import React, { FC } from "react";

interface ChatFollowUpProps {
  text?: string;
  onFollowUpClicked?: (text: string | undefined) => void;
}

const ChatFollowUp: FC<ChatFollowUpProps> = ({ text, onFollowUpClicked }) => {
  const theme = useTheme()
  const elevationLevel = 2;
  return (   
      <Button variant="text"
        sx={{ background: theme.palette.primary.light,
          boxShadow: theme.shadows[elevationLevel],
          margin: "10px",
          '&:hover': {
            background:  theme.palette.primary.main,
            color: theme.palette.primary.contrastText
          },
          }} onClick={() => onFollowUpClicked?.(text)}>
        {text}
      </Button>
   
  );
};

ChatFollowUp.defaultProps = {
  text: "this is a question?",
};

export default ChatFollowUp;
