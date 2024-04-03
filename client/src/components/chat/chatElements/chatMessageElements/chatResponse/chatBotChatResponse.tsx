import { Box, Dialog, DialogContent, Grid, Typography } from "@mui/material";
import DOMPurify from "dompurify";
import React, { FC, useState } from "react";
import "../../../../../assets/styles.css";
import messageSample from "../../../../../model/messages/messageSample.json";
import ParentMessage, { Citation, MessageContent } from "../../../../../model/messages/messages";
import ChatCitation from "./chatResponseElements/chatCitation";
import ChatFollowUp from "./chatResponseElements/chatFollowUp";

//for default props
const jsonString = JSON.stringify(messageSample);
const sampleMessages = JSON.parse(jsonString) as MessageContent[];

interface ChatBotChatResponseProps {
  onFollowupClicked: (message: string) => void;
  message: string;
  follow_up_questions?: string[],
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
  const messageWithLineBreaks = message ? message.replace(/\n/g, '<br>') : "";
  const sanitizedHTML = DOMPurify.sanitize(messageWithLineBreaks);
  const labelsCol = 2;
  const openCitation = (path: string) => {
    setIframeSrc(path);
  };

  const closeIframe = () => {
    setIframeSrc(null);
  };
  return (
    <Box>
      <Typography variant="body1">
        {sanitizedHTML}
      </Typography>
      <Box height="20px"></Box>
      <Grid container spacing={3} direction={'row'}>
        <Grid item xs={labelsCol} direction={'row'}>
          <Typography variant="subtitle1">Citations: </Typography>


        </Grid>
        <Grid item xs={(12-labelsCol)}>
          {message && citations && citations.length > 0 && (
            <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
              {citations.slice(0, 3).map((citation, index) => (
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
          )}
        </Grid>
        <Grid item xs={labelsCol}>
          <Typography variant="subtitle1">Follow-up Questions: </Typography>
        </Grid>
        <Grid item xs={(12-labelsCol)}>
          {message && follow_up_questions && follow_up_questions.length > 0 && (
            <Grid className="chatBotChatReferences" item xs={12}>

              <Grid container spacing={2} direction={'row'}>

                {follow_up_questions.slice(0, 4).map((followup, index) => (
                  <Grid item xs={6} key={index}>
                    <ChatFollowUp
                      text={followup}
                      onFollowUpClicked={(text) => {
                        console.log("question in parent:", text);
                        text && onFollowupClicked(text);
                      }}
                    />
                  </Grid>
                ))}
              </Grid>

            </Grid>
          )}
        </Grid>
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
