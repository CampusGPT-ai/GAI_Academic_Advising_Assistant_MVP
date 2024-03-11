import SendIcon from "@mui/icons-material/Send";
import Box from "@mui/material/Box";
import Grid from '@mui/material/Grid';
import { useTheme } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import React, { ChangeEvent, FC, KeyboardEvent, useState } from "react";
import AppStatus from "../../../model/conversation/statusMessages";

interface ChatInputProps {
  sendChat: (text: string) => void;
  appStatus: AppStatus;
}

/**
 * Renders a chat input component.
 * @param {Object} props - The component props.
 * @param {Function} props.sendChat - The function to send a chat message.
 * @param {boolean} props.isLoading - A flag indicating if the component is in a loading state.
 * @returns {JSX.Element} - The rendered component.
 */
const ChatInput: FC<ChatInputProps> = ({ sendChat, appStatus }) => {
  const [message, setMessage] = useState("");
  const theme = useTheme();
  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setMessage(e.target.value);
  };

  const handleSendClick = () => {
    if (message.trim() !== "") {
      sendChat(message);
      setMessage("");
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {  // Check for Enter key without Shift key
      e.preventDefault();  // Prevent default to avoid line break in TextField
      handleSendClick();
    }
  };

  const isLoading = appStatus!==AppStatus.Idle;

  return (
    <Box  sx={{ mt: 4 }} width="90%">

      <Grid container spacing={1} width="100%" mt={1}>
        <Grid item xs={10}>
        <TextField
        placeholder="What's on your mind today?"
        variant="outlined"
        value={message}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        fullWidth
        disabled={isLoading}
      />
        </Grid>
        <Grid item xs={2} sx={{display: "flex", justifyContent: "start"}}>
      <IconButton onClick={handleSendClick} disabled={isLoading} aria-label="Send icon">
        <SendIcon fontSize="medium" color="primary"/>
      </IconButton>
      </Grid>
      </Grid>
    </Box>
  );
};

export default ChatInput;
