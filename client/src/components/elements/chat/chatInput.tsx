import SendIcon from "@mui/icons-material/Send";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import { ChangeEvent, FC, KeyboardEvent, useState } from "react";

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
    <Box className="chatInputContainer" sx={{ mt: 4 }}>
      <TextField
        className="chatInput"
        placeholder="Type a new question (e.g. How can I get help picking courses for next semester?)"
        variant="standard"
        value={message}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        fullWidth
        disabled={isLoading}
      />
      <IconButton onClick={handleSendClick} disabled={isLoading}>
        <SendIcon />
      </IconButton>
    </Box>
  );
};

export default ChatInput;
