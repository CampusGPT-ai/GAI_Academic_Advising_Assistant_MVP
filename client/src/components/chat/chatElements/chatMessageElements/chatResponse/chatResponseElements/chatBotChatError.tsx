import { Warning } from "@mui/icons-material";
import { Box, Button, Grid, Typography } from "@mui/material";
import React, { FC } from "react";
import "../../../assets/styles.css";



interface ChatBotChatErrorProps {
  onRetry?: () => void;
  error?: string;
}

const ChatBotChatError: FC<ChatBotChatErrorProps> = ({
  onRetry,
  error,
}) => {
  return (

          <Box className="chatBotChatError">
            <Grid
              container
              direction="row"
              justifyContent="center"
              alignItems="start"
              marginBottom={1}
            >
              <Warning
                aria-hidden="true"
                aria-label="Error icon"
                sx={{ color: "error.main", fontSize: 20}}
              />
              <Typography variant="body1" color="warning">
                &nbsp;{error}
              </Typography>
            </Grid>
            <Button variant="contained" color="primary" onClick={onRetry}>
              Retry
            </Button>
          </Box>
        )
};

ChatBotChatError.defaultProps = {

  error: "this is some error text",

};

export default ChatBotChatError;
