//src/components/pages/index.tsxfetchmessages
// TODO: get rid of is loading in favor of app status
import React, { FC, useEffect, useRef, useState } from "react";
import fetchMessageHistory from "../api/fetchMessages";
import Conversation from "../model/conversation/conversations";
import { MessageSimple } from "../model/messages/messages";
import Footer from "../components/footer/footer";
import Chat from "./chat";
import { Box, Container} from "@mui/material";
import { BaseUrl } from "../api/baseURL";
import { useMsal, useIsAuthenticated} from "@azure/msal-react";
import useStreamData from "../hooks/botResponse";
import useAccountData from "../hooks/userData";
import AppBar from '@mui/material/AppBar';
import { useTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import DrawerContainer from "../components/menuDrawer/drawerContainer";
import AppStatus from "../model/conversation/statusMessages";

const MainPage: FC = () => {

  interface detectHistoryRefresh {
    isNewConversation: boolean,
    isMessageLoaded: boolean,
  }

  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [messageHistory, setMessageHistory] = useState<MessageSimple[]>();
  const [isError, setIsError] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<Conversation>();
  const [apiUrl, setApiUrl] = useState<string>();
  const [conversationRefreshFlag, setRefreshFlag] = useState<detectHistoryRefresh>({isNewConversation: false, isMessageLoaded: false});

  // track current values for state changes
  const [appStatus, setAppStatus] = useState<AppStatus>(AppStatus.Idle);
  const conversationRef = useRef<Conversation>();

  //TODO: I think I can get rid of this 
  const currentAnswerRef = useRef<Conversation>();
  

  
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
  const { streamingMessage, citations, followups, isStreaming, streamingError } = useStreamData(apiUrl, setSelectedConversation, getSelectedConversationMessages);
  const { userSession, sampleQuestions, conversations, initDataError, dataStatus, conversationHistoryFlag } = useAccountData({accounts, instance, isAuthenticated, inProgress, refreshFlag: conversationRefreshFlag})

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
   * Resets the selected conversation state.
   */
  const resetConversation = () => {
    setSelectedConversation(undefined);
    setMessageHistory(undefined);
  };


  const handleUserQuestion = async (input: string) => {
    if (userSession) {
    if (selectedConversation && selectedConversation.id) {
      setApiUrl(`${BaseUrl()}/users/${userSession}/conversations/${selectedConversation.id}/chat/${input}`);
    } else     
    {
      setRefreshFlag({
        isNewConversation: true,
        isMessageLoaded: false
      });
      setApiUrl(`${BaseUrl()}/users/${userSession}/conversations/0/chat/${input}`);
    }
  }
  };

  useEffect(() => {
    // if new conversation with Message History, flag to reload history
    if (
      conversationRefreshFlag.isNewConversation &&
      appStatus === AppStatus.Idle &&
      messageHistory
      ){
        setRefreshFlag({
          isNewConversation: true,
          isMessageLoaded: true
        })
      }
  }, [conversationRefreshFlag, messageHistory, appStatus])

  useEffect(()=>{
    // reset loading flag when conversation history is updated
    conversationHistoryFlag.isHistoryUpdated  &&         
    setRefreshFlag({
      isNewConversation: false,
      isMessageLoaded: false
    })
  },[conversationHistoryFlag])


  useEffect(() => {
    //change triggered by conversation change
    if (selectedConversation && selectedConversation !== conversationRef.current) {
        if(!isStreaming && selectedConversation){
          getSelectedConversationMessages()
          appStatus != AppStatus.Idle && setAppStatus(AppStatus.Idle)
          console.log(`detected conversation change while not streaming.  Resetting chat history for new conversation`)
        }
        conversationRef.current === selectedConversation
    }
    else {
      if (!isStreaming && appStatus === AppStatus.GeneratingChatResponse)
      {
          setAppStatus(AppStatus.Idle)
        }
      }
    

    isStreaming && setAppStatus(AppStatus.GeneratingChatResponse)

  },[isStreaming, selectedConversation])

  useEffect(()=>{
    setAppStatus(dataStatus)
  },[dataStatus])

  useEffect(()=>{
    console.log(`detected App Status change.  setting app status to ${appStatus}`)
  },[appStatus])

  useEffect(() => {
    (initDataError || streamingError) && setIsError(true)
    isError && console.error(`ERROR DETECTED: Implement Error Handling`)
    isError && setAppStatus(AppStatus.Error)
  },[isError, initDataError, streamingError] )

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
          <Box display="flex" width="100%" justifyContent={"center"} mt={2}>
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
          component="main"
          display="flex"
          flexGrow={1}
          sx={{
            mainContentStyles
          }}
        >
          <Chat
            appStatus={appStatus}
            sampleQuestions={sampleQuestions}
            sendChatClicked={handleUserQuestion}
            messageHistory={messageHistory}
            chatResponse={streamingMessage}
            currentAnswerRef={currentAnswerRef}
            follow_up_questions={followups}
            citations={citations}
            chatWidth={"100%"}
          /></Box>
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
