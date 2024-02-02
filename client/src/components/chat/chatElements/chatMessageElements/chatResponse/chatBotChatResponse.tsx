import { Box, Dialog, DialogContent, Grid, Typography } from "@mui/material";
import DOMPurify from "dompurify";
import React, { FC, useState } from "react";
import "../../../../../assets/styles.css";
import messageSample from "../../../../../model/messages/messageSample.json";
import ParentMessage, {Citation, Followup, Message} from "../../../../../model/messages/messages";
import ChatCitation from "./chatResponseElements/chatCitation";
import ChatFollowUp from "./chatResponseElements/chatFollowUp";

//for default props
const jsonString = JSON.stringify(messageSample);
const sampleMessages = JSON.parse(jsonString) as Message[];

interface ChatBotChatResponseProps {
  onFollowupClicked: (message: string) => void;
  message: Message;
  follow_up_questions?: Followup[],
  citations?: Citation[]
  currentAnswerRef?: React.MutableRefObject<any>;
}

const ChatBotChatResponse: FC<ChatBotChatResponseProps> = ({
  message,
  follow_up_questions,
  citations,
  currentAnswerRef,
  onFollowupClicked,
}) => {
  const [iframeSrc, setIframeSrc] = useState<string | null>(null);
  const messageWithLineBreaks = message ? message.message.replace(/\n/g, '<br>') : "";
  const sanitizedHTML = DOMPurify.sanitize(messageWithLineBreaks);

  const openCitation = (path: string) => {
    setIframeSrc(path);
  };

  const closeIframe = () => {
    setIframeSrc(null);
  };
  return (
    <Box>
      <Typography variant="body1" ref={currentAnswerRef}>
        <span
          dangerouslySetInnerHTML={{ __html: message ? sanitizedHTML : "" }}
        />
      </Typography>
      <Grid container spacing={1}>
        {message && citations && citations.length > 0 && (
          <Grid className="chatBotChatReferences" item xs={12}>
            <Typography variant="subtitle1">Citations: </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
            {citations.map((citation, index) => (
              <ChatCitation
                key={index}
                text={`${index + 1} ${citation.citation_text}`}
                path={citation.citation_path}
                onCitationClicked={(path) => {
                  console.log("Path in parent:", path);
                  path && openCitation(path);
                }}
              />
            ))}
            </Box>
          </Grid>
        )}
        {message && follow_up_questions && follow_up_questions.length > 0 && (
          <Grid className="chatBotChatReferences" item xs={12}>
            <Typography variant="subtitle1">Follow-up Questions: </Typography>

            {follow_up_questions.map((followup, index) => (
              <ChatFollowUp
                key={index}
                text={followup.question}
                onFollowUpClicked={(text) => {
                  console.log("question in parent:", text);
                  text && onFollowupClicked(text);
                }}
              />
            ))}
          </Grid>
        )}
      </Grid>

      {/* Render the Dialog with the iframe when iframeSrc is not null */}
      {iframeSrc && (
        <Dialog
          open={Boolean(iframeSrc)}
          onClose={closeIframe}
          maxWidth="lg"
          fullWidth
        >
          <DialogContent>
            {/* The iframe itself */}
            <iframe
              src={iframeSrc}
              title="Citation"
              frameBorder="0"
              width="100%"
              height="500px"
              allowFullScreen
            />
          </DialogContent>
        </Dialog>
      )}
    </Box>
  );
};

export default ChatBotChatResponse;
