import { Button, useTheme, Typography } from "@mui/material";
import React, { FC } from "react";

interface ChatFollowUpProps {
  text?: string;
  onFollowUpClicked?: (text: string | undefined) => void;
}

const ChatFollowUp: FC<ChatFollowUpProps> = ({ text, onFollowUpClicked }) => 
{
  const theme = useTheme()
  const elevationLevel = 2;
  console.log(`got follow up question for ${text}`)

  return (   
      <Button variant="text"
        sx={{ background: theme.palette.primary.light,
          textTransform: 'none',
          height: '100%',
          boxShadow: theme.shadows[elevationLevel],
          padding: "10px",
          m: '1',
          '&:hover': {
            background:  theme.palette.primary.main,
            color: theme.palette.primary.contrastText
          },
          }} onClick={() => onFollowUpClicked?.(text)}>
        <Typography variant="body1" textAlign={'left'}>{text}</Typography>
      </Button>
   
  );
};

ChatFollowUp.defaultProps = {
  text: "this is a question?",
};

export default ChatFollowUp;

