import { Button } from "@mui/material";
import React, { FC } from "react";

interface ChatFollowUpProps {
  text?: string;
  onFollowUpClicked?: (text: string | undefined) => void;
}

const ChatFollowUp: FC<ChatFollowUpProps> = ({ text, onFollowUpClicked }) => {
  return (   
      <Button variant="text" sx={{ background: "#000000", margin: "10px"}} onClick={() => onFollowUpClicked?.(text)}>
        {text}
      </Button>
   
  );
};

ChatFollowUp.defaultProps = {
  text: "this is a question?",
};

export default ChatFollowUp;
