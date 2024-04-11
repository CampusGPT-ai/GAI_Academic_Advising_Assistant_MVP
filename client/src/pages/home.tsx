//src/components/pages/index.tsxfetchmessages
// TODO: get rid of is loading in favor of app status
import React, { FC, useEffect, useRef, useState } from "react";
import fetchMessageHistory from "../api/fetchMessages";
import Conversation from "../model/conversation/conversations";
import { MessageSimple } from "../model/messages/messages";
import Footer from "../components/footer/footer";
import Chat from "./chat";
import { Box, Container, Grid, CircularProgress } from "@mui/material";
import { BaseUrl } from "../api/baseURL";
import { useMsal, useIsAuthenticated} from "@azure/msal-react";
import useAccountData from "../hooks/userData";
import useStreamDataNew from "../hooks/botResponseNew";
import AppBar from '@mui/material/AppBar';
import { useTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import DrawerContainer from "../components/menuDrawer/drawerContainer";
import AppStatus from "../model/conversation/statusMessages";
import ChatSampleQuestion from "../components/chat/chatElements/chatSampleQuestion";
import ChatInput from "../components/chat/chatElements/chatInput";
const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';
import ChatUserChat from "../components/chat/chatElements/chatMessageElements/chatUserChat";

const MainPage: FC = () => {
  // console.log("loading main page for auth type: ", AUTH_TYPE)

  interface detectHistoryRefresh {
    isNewConversation: boolean,
  }

  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [messageHistory, setMessageHistory] = useState<MessageSimple[]>();
  const [currentMessage, setCurrentMessage] = useState<MessageSimple>();
  const [currentResponse, setCurrentResponse] = useState<MessageSimple>();
  const [isError, setIsError] = useState(false);
  const [notification, setNotification] = useState<string>();
  const [selectedConversation, setSelectedConversation] = useState<Conversation>();
  const [apiUrl, setApiUrl] = useState<string>();
  const [refreshFlag, setRefreshFlag] = useState<Boolean>(false);
  const [newConversationFlag, setNewConversationFlag] = useState<Boolean>(false);
  const [userQuestion, setUserQuestion] = useState<string>();

  // track current values for state changes
  const [appStatus, setAppStatus] = useState<AppStatus>(AppStatus.Idle);
  const statusRef = useRef<AppStatus>(appStatus);
  const conversationRef = useRef<Conversation>();
  const messageHistoryRef = useRef<MessageSimple[]>();


  const currentAnswerRef = useRef<MessageSimple>();

  const getMessageHistory = async () => {
    if (userSession && selectedConversation && selectedConversation.id ) {
    try {
      // console.log("fetching message history from api")
      const result = await fetchMessageHistory({ user: userSession, conversationId: selectedConversation.id });
      if (result.type === 'messages') {
        setMessageHistory(result.data);
      } else if (result.type === 'info') {
        console.info("no conversations created yet")

      }
      
  } catch (error) {
    setIsError(true)
    console.error(`An error occurred while fetching conversations ${error}`);

  }
}
};
  
  // custom hooks 
  // TODO: Create provider for stream data for nested content
 const { taskId, message, question, risks, opportunities, isStreaming, streamingError } = useStreamDataNew(
  setAppStatus,
  apiUrl,
  setSelectedConversation,
  setIsError,
  setNotification)


  const { userSession, sampleQuestions, conversations, initDataError, conversationHistoryFlag } = useAccountData(
    refreshFlag, setRefreshFlag, setAppStatus)

  // console.log("loading main page")
  // console.log("selected conversation: ",JSON.stringify(selectedConversation))
  // console.log(`message history: ${JSON.stringify(messageHistory)}`)

  const theme = useTheme()
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [isClosing, setIsClosing] = React.useState(false);
  const drawerWidth = 240;

  const handleDrawerToggle = () => {
    if (!isClosing) {
      setMobileOpen(!mobileOpen);
    }
  };

  /**
   * Resets the selected conversation state if the new chat button is clicked
   */
  const resetConversation = () => {
    setRefreshFlag(false);
    setSelectedConversation(undefined);
    setMessageHistory(undefined);
    setCurrentMessage(undefined);
    setCurrentResponse(undefined);
    setAppStatus(AppStatus.Idle);
  };

  // when a new question is recieved, update the history
  const updateHistory = (message: MessageSimple) => {
    if (!messageHistory) {
      console.log("no message history - creating new history with message ", JSON.stringify(message), appStatus)
      setMessageHistory([message]);
    }
    else {
      console.log(`history before udpate: ${JSON.stringify(messageHistory)}, app Status: ${appStatus}`)
      setMessageHistory([...messageHistory, message]);
      console.log(`history after udpate: ${JSON.stringify(messageHistory)}, app Status: ${appStatus}`)
    }
  }


  const handleUserQuestion = async (input: string) => {
    console.log(`handle user question app Status: ${appStatus}`)
    const userMessage : MessageSimple = {role: "user", message: input, created_at: { $date: Date.now() }};
    updateHistory(userMessage);

    if (userSession) {
    setUserQuestion(input)
    setAppStatus(AppStatus.GeneratingChatResponse)
  }
  };

  // this effect should only run if there is a change in the app status.  It does the following:
  // 1.  If the app status is generating chat response, it sets the api url to the appropriate value
  // 2.  If the app status is getting message history, it fetches the message history
  // 3.  If the app status is idle, it sets the api url to undefined
  useEffect(() => {
// first ensure there has been a true status change.  
if (appStatus !== statusRef.current) {
    statusRef.current = appStatus;
    if (appStatus === AppStatus.GeneratingChatResponse && userQuestion) {
      if (selectedConversation && selectedConversation.id) {
          setApiUrl(`${BaseUrl()}/users/${userSession}/conversations/${selectedConversation.id}/chat_new/${userQuestion}`);
        } else     
        {
          console.log("checking app status before setting refresh flag on line 153: ", appStatus)
          setNewConversationFlag(true);
          setApiUrl(`${BaseUrl()}/users/${userSession}/conversations/0/chat_new/${userQuestion}`);
        }
    }

    if (appStatus === AppStatus.Idle || appStatus === AppStatus.Error) {
      // only refresh history list when the app is idle
      newConversationFlag && setRefreshFlag(true);
      setNewConversationFlag(false)
      setApiUrl(undefined);
    }

    if (selectedConversation 
      && userSession 
      && appStatus===AppStatus.GettingMessageHistory) {
        getMessageHistory();
        conversationRef.current = selectedConversation;
      }
  }
}, [newConversationFlag, appStatus, userQuestion, selectedConversation])

// this effect sets the app status to get message history if the conversation changes and app status is currently idle (only runs when idle)
useEffect(() =>{
  if (selectedConversation && appStatus === AppStatus.Idle && selectedConversation !== conversationRef.current) {
    conversationRef.current = selectedConversation;
    setAppStatus(AppStatus.GettingMessageHistory)
  }
},[selectedConversation, appStatus])

// this effect sets the app status to idle when the message history is updated (Idle is the default status when no other status is set, and indicates the app is ready to process new requests)
useEffect(() => {
  if (messageHistory && appStatus === AppStatus.GettingMessageHistory && messageHistory !== messageHistoryRef.current) {
    messageHistoryRef.current = messageHistory;
    setAppStatus(AppStatus.Idle)
  }
},[messageHistory])

  useEffect(() => {
    if (message !== undefined && question !== undefined && message !== "" && question !== "") { 
      console.log("message and question recieved: ", message, question)

      const response : MessageSimple = {role: "system", message: message, created_at: { $date: Date.now() }};
      console.log(`creating simple message with ${JSON.stringify(response)}`)
      updateHistory(response);
      
      const followup: MessageSimple = {role: "system", message: question, created_at: { $date: Date.now() }};
      console.log(`creating simple message with ${JSON.stringify(followup)}`)
      updateHistory(followup);


  }},[message, question]
  )

  useEffect(() => {
    (initDataError || streamingError) && setIsError(true)
    isError && console.error(`ERROR DETECTED: ${JSON.stringify(streamingError)}`)
    isError && setAppStatus(AppStatus.Error)
    
  },[isError, initDataError, streamingError] )

  const mainContentStyles = {
    flexGrow: 1,
    p: 3,
    width: { sm: `calc(100% - ${drawerWidth}px)` },
    maxHeight: { sm: `calc(100% - 600px)` },
    mt: { xs: 8, sm: 0 }, // Adjust the margin top to align with the AppBar height.
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    ...(mobileOpen && {
      width: `calc(100% - ${drawerWidth}px)`,
      ml: `${drawerWidth}px`,
      transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
    }),
  };


  return (
    <Box sx={{ display: 'flex', flexDirection: 'column',height: '100vh', maxWidth: '1200px', }}>
      <CssBaseline />
      <AppBar
        position='relative'
        elevation={0}
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          maxWidth: '100%',
          ml: { sm: `${drawerWidth}px` },

          backgroundColor: "#fff"
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{
              mr: 2,
              display: { sm: 'none' },

            }}
          >
            <MenuIcon />
          </IconButton>
          <Box display="flex" width="100%" justifyContent={"center"} mt={2} mb={2}>
            <Typography variant="h2" noWrap component="div" color="#000">
              Your personal <Typography variant="h1" color="primary">AI Assistant </Typography>
              TESTING: {appStatus}
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

  {
     <DrawerContainer conversationList={conversations}
     conversationFlag={conversationHistoryFlag.userHasHistory}
       handleSelectConversation={setSelectedConversation}
        resetConversation={resetConversation}
         account={accounts[0]}/>
  }      
    
      {/**main page content here */}
      <Container component="main" sx={{
        display: "flex",
        flexGrow: 1,
        maxHeight: "80%",
        marginLeft: { sm: `${drawerWidth}px`, xs: 0 },
        width: { sm: `calc(100% - ${drawerWidth}px)`, xs: "100%" },
        marginRight: "0"
      }}>
        <Box
          display="flex"
          flexGrow={1}
          maxHeight={"100%"}
        >
         <Chat 
           appStatus = {appStatus}
           isError = {isError}
           errMessage = {streamingError}
           notifications = {notification}
           sampleQuestions = {sampleQuestions}
           chatResponse = {message}
           sendChatClicked = {handleUserQuestion}
           messageHistory = {messageHistory}
           currentAnswerRef = {currentAnswerRef}
           chatWidth = "70vw"/>
          </Box>
      </Container>

      <Box component="footer" sx={{
        width: { sm: `calc(100% - ${drawerWidth}px)` },
        maxWidth: '100%',
        ml: { sm: `${drawerWidth}px` },
      }}>
        <Footer></Footer>
      </Box>
    </Box>

  );
}

export default MainPage;
