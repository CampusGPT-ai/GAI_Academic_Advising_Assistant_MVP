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
import useStreamData from "../hooks/botResponse";
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
import ChatSampleQuestion from "../components/chat/chatElements/chatMessageElements/chatSampleQuestion";
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
  const [newConversationFlag, setRefreshFlag] = useState<Boolean>(false);

  // track current values for state changes
  const [appStatus, setAppStatus] = useState<AppStatus>(AppStatus.Idle);
  const conversationRef = useRef<Conversation>();

  //TODO: I think I can get rid of this 
  const currentAnswerRef = useRef<MessageSimple>();
  

  
  /**
   * Fetches and sets the selected conversation.
   */
  const getSelectedConversationMessages = async () => {
    setAppStatus(AppStatus.GettingMessageHistory)
    try {
      if (selectedConversation && userSession) {
        console.log("fetching message history from api")
        const result = await fetchMessageHistory({ user: userSession, conversationId: selectedConversation.id });
        if (result.type === 'messages') {
          setMessageHistory(result.data);
        } else if (result.type === 'info') {
          console.info("no conversations created yet")

        }
        }
    } catch (error) {
      setIsError(true)
      console.error(`An error occurred while fetching conversations ${error}`);

    }
    finally {
      setAppStatus(AppStatus.Idle)
    }
  };

  
  // custom hooks 
  // TODO: Create provider for stream data for nested content
 const { message, risks, opportunities, isStreaming, streamingError } = useStreamDataNew(
  setAppStatus,
  apiUrl,
  setSelectedConversation,
  getSelectedConversationMessages,
  setIsError,
  setNotification)

  const { userSession, sampleQuestions, conversations, initDataError, conversationHistoryFlag } = useAccountData(
    {newConversationFlag, setAppStatus})

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
    setSelectedConversation(undefined);
    setMessageHistory(undefined);
    setCurrentMessage(undefined);
    setCurrentResponse(undefined);
  };

  // when a new question is recieved, update the history
  const updateHistory = (message: MessageSimple) => {
    if (!messageHistory) {
      console.log("no message history - creating new history")
      setMessageHistory([message]);
    }
    else {
      console.log("updating history with ", JSON.stringify(message))  
      setMessageHistory([...messageHistory, message]);
    }
  }


  const handleUserQuestion = async (input: string) => {

    const userMessage : MessageSimple = {role: "user", message: input, created_at: { $date: Date.now() }};
    updateHistory(userMessage);

    if (userSession) {
    if (selectedConversation && selectedConversation.id) {
      setApiUrl(`${BaseUrl()}/users/${userSession}/conversations/${selectedConversation.id}/chat_new/${input}`);
    } else     
    {
      setRefreshFlag(true);
      setApiUrl(`${BaseUrl()}/users/${userSession}/conversations/0/chat_new/${input}`);
    }
  }
  };

  useEffect(() => {
    // if new conversation with Message History, flag to reload history
    if (
      newConversationFlag &&
      appStatus === AppStatus.Idle
      ){
        // refresh conversation list to grab the latest. 
        // set the selected conversation to the latest
      }
  }, [newConversationFlag, appStatus])

  useEffect(() => {
    //change triggered by conversation change

    if (newConversationFlag && selectedConversation && selectedConversation !== conversationRef.current)
    {
      setRefreshFlag(false)
    }
    else if (selectedConversation && selectedConversation !== conversationRef.current) {
          getSelectedConversationMessages()
          appStatus != AppStatus.Idle && setAppStatus(AppStatus.Idle)  
    }

    conversationRef.current === selectedConversation

  },[selectedConversation])

  useEffect(() => {
    console.log("message recieved: ", message)
    if (message) { 
      const response : MessageSimple = {role: "system", message: message, created_at: { $date: Date.now() }};
      if (currentAnswerRef.current === undefined) {
        console.log("current answer is undefined - updating history")
        updateHistory(response);
        currentAnswerRef.current = response;
      }
      else
      if (currentAnswerRef.current && currentAnswerRef.current.message !== response.message) {
        console.log("current answer is different - updating history")
        updateHistory(response);
        currentAnswerRef.current = response;
      }
  }},[message]
  )


  useEffect(() => {
    (initDataError || streamingError) && setIsError(true)
    isError && console.error(`ERROR DETECTED: ${JSON.stringify(streamingError)}`)
    isError && setAppStatus(AppStatus.Error)
  },[isError, initDataError, streamingError] )

  useEffect(() => {
    console.log("detected change in selected conversation", JSON.stringify(selectedConversation))
  }, [selectedConversation])

  const mainContentStyles = {
    flexGrow: 1,
    p: 3,
    width: { sm: `calc(100% - ${drawerWidth}px)` },
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
        marginLeft: { sm: `${drawerWidth}px`, xs: 0 },
        width: { sm: `calc(100% - ${drawerWidth}px)`, xs: "100%" },
        marginRight: "0"
      }}>
        <Box
          display="flex"
          flexGrow={1}
          sx={{
            mainContentStyles
          }}
        >
         <Chat 
           appStatus = {appStatus}
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
