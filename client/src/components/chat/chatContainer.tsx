import { Box, useTheme, Grid, CircularProgress } from "@mui/material";
import React, { FC, useEffect, useState } from "react";
import "../../assets/styles.css";
import messageSample from "../../model/messages/messageSample.json";
import ParentMessage, {Citation, MessageSimple} from "../../model/messages/messages";
import ChatInput from "./chatElements/chatInput";
import ChatMessages from "./chatElements/chatMessageContainer";
import ChatSampleQuestion from "./chatElements/chatSampleQuestion";
import AppStatus from "../../model/conversation/statusMessages";
import { Outcomes } from "../../api/fetchOutcomes";
/**
 * this component is the active chat component that is displayed when the user is in a chat.
 * it renders chat messages based on conversation history, and sends new questions back to the post request, 
 * either from clicking on a sample question or typing in the input box.
 * 
 */
/**
 * Props for the ChatActive component.
 * @interface
 * @property {boolean} isLoading - Indicates if the chat is currently loading.
 * @property {boolean} [isError] - Indicates if there was an error while loading the chat.
 * @property {Array<Message>} messages - An array of messages in the chat.
 * @property {function} [onRetry] - A function to retry loading the chat in case of an error.
 * @property {string} [error] - The error message to display in case of an error.
 * @property {string} [convoTitle] - The title of the conversation.
 * @property {Array<string>} [sampleQuestions] - An array of sample questions to display.
 * @property {function} sendChatClicked - A function to handle sending a chat message.
 */
interface ChatActiveProps {
  chatResponse?: string;
  follow_up_questions?: string[];
  citations?: Citation[];
  messageHistory?: MessageSimple[];  //optional history on selected conversation
  appStatus: AppStatus;
  errMessage?: string;
  isError?: boolean;
  notifications?: string;
  sampleQuestions?: Array<string>;
  sendChatClicked: (text: string) => void;
  currentAnswerRef: React.MutableRefObject<any>;
  opportunities?: Outcomes[];
  currentUserQuestion?: string;
}[]

const ChatActive: FC<ChatActiveProps> = ({
  appStatus,
  errMessage,
  sampleQuestions,
  messageHistory,
  isError,
  sendChatClicked,
  currentAnswerRef,
  opportunities,
  currentUserQuestion,
}) => {
  
  const [userQuestion, setUserQuestion] = useState('');

  //console.log(`user questions is set to ${userQuestion} with ${appStatus}`);
  /**
   * Sets the message state to the input text.
   * @param inputText - The text to set as the message state.
   */
  const handleSendClick = (inputText: string) => {
    // console.log(`sending chat from send clicked with ${inputText}`);
    appStatus === AppStatus.Idle && sendChatClicked(inputText);
    setUserQuestion(inputText);
  };

  /**
   * Sets the message state to the provided question text.
   * @param questionText - The text of the question to set as the message.
   */
  const handleQuestionClick = (questionText: string) => {
    // console.log(`sample question clicked: ${questionText}`);
    appStatus === AppStatus.Idle && sendChatClicked(questionText)
    setUserQuestion(questionText);
  };

  const handleRetry = () => {
    // console.log(`retrying chat due to error`)
    userQuestion != '' && userQuestion && sendChatClicked(userQuestion)
  }



  // console.log(`generating chat history with ${JSON.stringify(messageHistory)}, app status is ${appStatus}`)
  return (
    
    <Box sx={{alignItems: "center", 
    width: "95%", p: 2,
    display: "flex",
    flexGrow: 1,
    height: "100%",
    flexDirection: "column",
    mt: 2,
    borderRadius: 1, 
    justifyContent: "space-between"
    }}>
      {(messageHistory && messageHistory.length>0) ? (
        <>
          <ChatMessages
            userQuestion={userQuestion}
            messageHistory={messageHistory}
            appStatus={appStatus}
            errMessage={errMessage}
            onRetry={handleRetry}
            isError={isError}
            currentAnswerRef={currentAnswerRef}
            opportunities={opportunities}
            onFollowUpClicked={handleQuestionClick}
          />
        </>
      ) : (
        <>

          <Grid container spacing={2} direction={'row'}>
          {sampleQuestions && sampleQuestions.map((question, index) => (
            <Grid item xs={12} sm={6} key={index} >

                <ChatSampleQuestion onSampleQuestionsClicked={handleQuestionClick} text={question} appStatus={appStatus}/>
            </Grid>
            ))}
            {!sampleQuestions &&
            <Box width={'100%'} display={"flex"} justifyContent={"center"}>
              <CircularProgress
              size={20}
              thickness={5}
              style={{ marginLeft: 10 }}
              aria-label="loading sample questions"
            /> </Box>}
          </Grid>
          
    
        </>
      )}
      <ChatInput 
      sendChat={handleSendClick}
      appStatus={appStatus}></ChatInput>
    </Box>
  );
  
};

export default ChatActive;
