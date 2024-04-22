//src/components/pages/index.tsxfetchmessages

import React, { FC, useEffect, useRef, useState } from "react";
import fetchMessageHistory from "../api/fetchMessages";
import Conversation from "../model/conversation/conversations";
import { MessageSimple } from "../model/messages/messages";
import Footer from "../components/footer/footer";
import Chat from "./chat";
import { Box, Container, } from "@mui/material";
import { useMsal } from "@azure/msal-react";
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
const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';
import useQnAData from "../api/fetchQnA";
import { Outcomes } from "../api/fetchOutcomes";
import useGraphData from "../api/fetchOutcomes";

const MainPage: FC = () => {

  const { accounts } = useMsal();
  const [messageHistory, setMessageHistory] = useState<MessageSimple[]>();
  const [isError, setIsError] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<Conversation>();
  const [refreshFlag, setRefreshFlag] = useState<Boolean>(false);
  const [newConversationFlag, setNewConversationFlag] = useState<Boolean>(false);
  const [userQuestion, setUserQuestion] = useState<string>();
  const [appStatus, setAppStatus] = useState<AppStatus>(AppStatus.Idle);
  const statusRef = useRef<AppStatus>(appStatus);
  const conversationRef = useRef<Conversation>();
  const messageHistoryRef = useRef<MessageSimple[]>();
  const responseRef = useRef<string>();
  const questionRef = useRef<string>();
  const [outcomes, setOutcomes] = useState<Outcomes[]>();

  const currentAnswerRef = useRef<MessageSimple>();


  const getMessageHistory = async () => {
    if (userSession && selectedConversation && selectedConversation.id) {
      try {
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

  const { userSession, sampleQuestions, conversations, initDataError, conversationHistoryFlag } = useAccountData(
    refreshFlag, setRefreshFlag, setAppStatus)

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
    setUserQuestion(undefined);
    setSelectedConversation(undefined);
    setMessageHistory(undefined);
    responseRef.current = undefined;
    questionRef.current = undefined;
    setAppStatus(AppStatus.Idle);
  };

  // when a new question is recieved, update the history
  const updateHistory = (message: MessageSimple) => {
    if (message) { // Ensure message is not undefined or null
      console.log("Received message: ", JSON.stringify(message));
      setMessageHistory(prevHistory => {
        // If prevHistory is undefined, start with an empty array
        const history = prevHistory || [];
        return [...history, message];
      });
    } else {
      console.error("Attempted to update history with undefined or null message");
    }
  };

  const handleUserQuestion = async (input: string) => {
    console.log(`handle user question with app Status: ${appStatus}`)
    const userMessage: MessageSimple = { role: "user", message: input, created_at: { $date: Date.now() } };
    updateHistory(userMessage);
    if (userSession) {
      setUserQuestion(input)
    }
  };

  useQnAData(userQuestion, userSession, selectedConversation?.id, setSelectedConversation, updateHistory, setAppStatus, setNewConversationFlag);
  const {risks, opportunities} = useGraphData(selectedConversation?.topic, userSession)
  // this effect should only run if there is a change in the app status.  It does the following:
  // 1.  If the app status is generating chat response, it sets the api url to the appropriate value
  // 2.  If the app status is getting message history, it fetches the message history
  // 3.  If the app status is idle, it sets the api url to undefined
  useEffect(() => {

    console.log(`app status use effect triggered with ${appStatus} 
      and ref is ${statusRef.current} and user question is ${userQuestion} 
      and selected conversation is ${JSON.stringify(selectedConversation)} 
      and new conversation flag is ${newConversationFlag}`)

    if (appStatus !== statusRef.current) {
      statusRef.current = appStatus;

      if (appStatus !== AppStatus.Idle && appStatus !== AppStatus.Error) {
        setIsError(false);
      }
    }

    if (appStatus === AppStatus.Idle || appStatus === AppStatus.Error) {
      if (newConversationFlag) {
        setNewConversationFlag(false)
        setRefreshFlag(true);
      }
    }
    if (selectedConversation
      && userSession
      && appStatus === AppStatus.GettingMessageHistory) {
      getMessageHistory();
      if (selectedConversation !== conversationRef.current) {
        conversationRef.current = selectedConversation;
      }
    }
  }, [appStatus, selectedConversation])

  // reset status when questions load
  useEffect(() => {
    if (sampleQuestions && appStatus === AppStatus.GettingQuestions) { setAppStatus(AppStatus.Idle) }
  }, [sampleQuestions])

  // this effect sets the app status to get message history if the conversation changes and app status is currently idle (only runs when idle)
  useEffect(() => {

    if (selectedConversation && selectedConversation !== conversationRef.current) {
      console.log(`Updating conversation history with new conversation ID ${selectedConversation.id}`)
      conversationRef.current = selectedConversation;
      setAppStatus(AppStatus.GettingMessageHistory)
    }
  }, [selectedConversation])

  // this effect sets the app status to idle when the message history is updated (Idle is the default status when no other status is set, and indicates the app is ready to process new requests)
  useEffect(() => {
    if (messageHistory && appStatus === AppStatus.GettingMessageHistory && messageHistory !== messageHistoryRef.current) {
      messageHistoryRef.current = messageHistory;
      setAppStatus(AppStatus.Idle)
    }
  }, [messageHistory, appStatus])

  useEffect(() => {
    (initDataError) && setIsError(true)
    isError && setAppStatus(AppStatus.Error)

  }, [isError, initDataError])

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
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', maxWidth: '1200px', }}>
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
          <Box display="flex" width="100%" justifyContent="center" flexDirection="row" mt={2} mb={2}>
            <Typography variant="h2" noWrap component="div" color="#000" style={{ display: 'flex', alignItems: 'center' }}>
              Your personal{' '}
              <Typography variant="h1" component="span" color="primary">
                &nbsp;AI Assistant
              </Typography>
            </Typography>
          </Box>


        </Toolbar>
      </AppBar>

      {
        <DrawerContainer conversationList={conversations}
          conversationFlag={conversationHistoryFlag.userHasHistory}
          handleSelectConversation={setSelectedConversation}
          resetConversation={resetConversation}
          account={accounts[0]} />
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
            appStatus={appStatus}
            isError={isError}
            sampleQuestions={sampleQuestions}
            sendChatClicked={handleUserQuestion}
            messageHistory={messageHistory}
            currentAnswerRef={currentAnswerRef}
            chatWidth="70vw"
            opportunities={opportunities} />
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
