import { Button, Grid, Typography, useTheme } from "@mui/material";
import React, { FC } from "react";
import "../../assets/styles.css";

/**
 * Props for the ChatHistoryHeader component.
 */
interface ChatHistoryHeaderProps {
  /**
   * Function to create a new chat.
   */
  newChat: () => void;
}

const ChatHistoryHeader: FC<ChatHistoryHeaderProps> = ({ newChat }) => {
  const theme = useTheme();
  return (
    <Grid
      className="chatHistoryHeader"
      container
      sx={{
        backgroundColor: (theme) => theme.palette.primary.main,
        p: 2,
      }}
    >
      <Grid item xs={6}>
        <Typography
          variant="h6"
          sx={{ color: (theme) => theme.palette.primary.contrastText }}
        >
          Chat History
        </Typography>
      </Grid>
      <Grid item xs={6}>
        <Button
          variant="contained"
          onClick={newChat}

        >
          New Chat
        </Button>
      </Grid>
    </Grid>
  );
};

export default ChatHistoryHeader;
