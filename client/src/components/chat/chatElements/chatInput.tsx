import SendIcon from "@mui/icons-material/Send";
import Box from "@mui/material/Box";
import Grid from '@mui/material/Grid';
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import React, { ChangeEvent, FC, KeyboardEvent, useState } from "react";
import TipsAndUpdatesOutlinedIcon from '@mui/icons-material/TipsAndUpdatesOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import DifferenceOutlinedIcon from '@mui/icons-material/DifferenceOutlined';
interface ChatInputProps {
  sendChat: (text: string) => void;
  isLoading: boolean;
}

/**
 * Renders a chat input component.
 * @param {Object} props - The component props.
 * @param {Function} props.sendChat - The function to send a chat message.
 * @param {boolean} props.isLoading - A flag indicating if the component is in a loading state.
 * @returns {JSX.Element} - The rendered component.
 */
const ChatInput: FC<ChatInputProps> = ({ sendChat, isLoading }) => {
  const [message, setMessage] = useState("");

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

  return (
    <Box  sx={{ mt: 4 }} width="60%">
      <TextField
        placeholder="Type your question to get started."
        variant="standard"
        value={message}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        fullWidth
        disabled={isLoading}
      />
      <Grid container width="100%" mt={1}>
        <Grid item xs={6} sx={{display: "flex", justifyContent: "start"}} >
        <IconButton onClick={handleSendClick} disabled={isLoading}>
        <TipsAndUpdatesOutlinedIcon fontSize="large" />        
      </IconButton>
      <IconButton onClick={handleSendClick} disabled={isLoading}>
      <HistoryOutlinedIcon fontSize="large"></HistoryOutlinedIcon>
      </IconButton>
      <IconButton onClick={handleSendClick} disabled={isLoading}>
      <DifferenceOutlinedIcon fontSize="large"></DifferenceOutlinedIcon>
      </IconButton>
        </Grid>
        <Grid item xs={6} sx={{display: "flex", justifyContent: "end"}}>
      <IconButton onClick={handleSendClick} disabled={isLoading}>
        <SendIcon fontSize="large"/>
      </IconButton>
      </Grid>
      </Grid>
    </Box>
  );
};

export default ChatInput;
