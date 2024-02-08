import { Box, useTheme, Grid, CircularProgress } from "@mui/material";
import React, { FC, useEffect, useState } from "react";
import "../../assets/styles.css";
import messageSample from "../../model/messages/messageSample.json";
import ParentMessage, {Citation, MessageSimple} from "../../model/messages/messages";
import ChatInput from "./chatElements/chatInput";
import ChatMessages from "./chatElements/chatMessageContainer";
import ChatSampleQuestion from "./chatElements/chatMessageElements/chatSampleQuestion";

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
  isLoading: boolean; //can remove
  chatResponse?: string;
  follow_up_questions?: string[];
  citations?: Citation[];
  messageHistory?: MessageSimple[];  //optional history on selected conversation
  appStatus?: string;
  sampleQuestions?: Array<string>;
  sendChatClicked: (text: string) => void;
  currentAnswerRef: React.MutableRefObject<any>;
}[]

const ChatActive: FC<ChatActiveProps> = ({
  chatResponse,
  follow_up_questions,
  citations,
  isLoading,
  appStatus,
  sampleQuestions,
  messageHistory,
  sendChatClicked,
  currentAnswerRef,

}) => {
  
  const [userQuestion, setUserQuestion] = useState('');
  const theme = useTheme()
  //console.log(`user questions is set to ${userQuestion} with ${appStatus}`);
  /**
   * Sets the message state to the input text.
   * @param inputText - The text to set as the message state.
   */
  const handleSendClick = (inputText: string) => {
    setUserQuestion(inputText);
  };

  /**
   * Sets the message state to the provided question text.
   * @param questionText - The text of the question to set as the message.
   */
  const handleQuestionClick = (questionText: string) => {
    setUserQuestion(questionText)
  };

  const handleRetry = () => {
    userQuestion != '' && userQuestion && sendChatClicked(userQuestion)
  }

  /**
   * activates the call back function when the message state is changed.
   */
  useEffect(() => {
    if (userQuestion.trim() !== '' && userQuestion !== undefined) {
      sendChatClicked(userQuestion);
    }
  },[userQuestion])


  //console.log(`passing loading and error states.  loading: ${isLoading} error: ${isError}`)
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
      {((messageHistory && messageHistory.length>0) || appStatus === "GENERATING CHAT RESPONSE" ) ? (
        <>
          <ChatMessages
            userQuestion={userQuestion}
            chatResponse={chatResponse}
            follow_up_questions={follow_up_questions}
            citations={citations}
            messageHistory={messageHistory}
            isLoading={isLoading}
            appStatus={appStatus}
            onFollowupClicked={handleQuestionClick}
            onRetry={handleRetry}
            currentAnswerRef={currentAnswerRef}
          />
        </>
      ) : (
        <>

          <Grid container spacing={2} direction={'row'}>
          {sampleQuestions && sampleQuestions.map((question, index) => (
            <Grid item xs={12} sm={6} key={index} >

                <ChatSampleQuestion onSampleQuestionsClicked={handleQuestionClick} text={question} isLoading={isLoading}/>
            </Grid>
            ))}
            {!sampleQuestions && appStatus==="LOADING DATA" &&
            <Box width={'100%'} display={"flex"} justifyContent={"center"}>
              <CircularProgress
              size={20}
              thickness={5}
              style={{ marginLeft: 10 }}
            /> </Box>}
          </Grid>
          
    
        </>
      )}
      <ChatInput 
      sendChat={handleSendClick}
      isLoading={isLoading}></ChatInput>
    </Box>
  );
  
};

export default ChatActive;
