import { Box, Typography } from "@mui/material";
import DOMPurify from "dompurify";
import React, { FC } from "react";
import "../../../../../assets/styles.css";
import messageSample from "../../../../../model/messages/messageSample.json";

// For default props
const jsonString = JSON.stringify(messageSample);

interface ChatBotChatResponseProps {
  message: string;
}

const ChatBotChatResponse: FC<ChatBotChatResponseProps> = ({
  message,
}) => {
  const messageWithLineBreaks = message ? message.replace(/\n/g, '<br>') : "";
  // Add a hook to make all links open a new window
  DOMPurify.addHook('afterSanitizeAttributes', function (node) {
    // set all elements owning target to target=_blank
    if ('target' in node) {
      node.setAttribute('target', '_blank');
    }
    // set non-HTML/MathML links to xlink:show=new
    if (
      !node.hasAttribute('target') &&
      (node.hasAttribute('xlink:href') || node.hasAttribute('href'))
    ) {
      node.setAttribute('xlink:show', 'new');
    }
  });

  const sanitizedHTML = DOMPurify.sanitize(messageWithLineBreaks, { USE_PROFILES: { html: true } });

  // Use a div and dangerouslySetInnerHTML to render sanitized HTML
  return (
    <Box>
      <div
        dangerouslySetInnerHTML={{ __html: sanitizedHTML }}
        style={{ marginBottom: '20px' }} // Replaced the Box with height="20px" for spacing
      ></div>
    </Box>
  );
};

export default ChatBotChatResponse;
