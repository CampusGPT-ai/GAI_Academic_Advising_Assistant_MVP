import { Button, useTheme, Typography } from "@mui/material";
import React, { FC } from "react";

// Assuming Outcomes is an interface
interface Outcomes {
  name: string;
  description: string;
}

interface ChatFollowUpProps {
  text: Outcomes;
  onFollowUpClicked: (text: string) => void;
}

const ChatFollowUp: FC<ChatFollowUpProps> = ({
  text = { name: "This is a question?", description: "Name" }, // Default values as part of destructuring in the function parameters
  onFollowUpClicked,
}) => {
  const theme = useTheme();
  const elevationLevel = 2;

  return (
    <div>
    <Button
      variant="text"
      sx={{
        background: theme.palette.primary.light,
        textTransform: 'none',
        height: '100%',
        boxShadow: theme.shadows[elevationLevel],
        padding: "10px",
        m: '1',
        '&:hover': {
          background: theme.palette.primary.main,
          color: theme.palette.primary.contrastText,
        },
      }}
      onClick={() => onFollowUpClicked(text.description)}
    >
      <Typography variant="body1" textAlign={'left'}>{text.name}: {text.description}</Typography>
    </Button>
    <br></br>
    </div>
  );
};

export default ChatFollowUp;
