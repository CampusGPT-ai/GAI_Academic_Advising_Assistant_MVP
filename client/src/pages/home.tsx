//src/components/pages/index.tsxfetchmessages

import React, { FC, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import fetchConversations from "../api/fetchConversations";
import fetchMessageHistory from "../api/fetchMessages";
import Conversation from "../model/conversation/conversations";
import ParentMessage, { Citation, Timestamp, Followup } from "../model/messages/messages";
import Footer from "../components/footer/footer";
import Chat from "./chat";
import { Box, Container, Divider, Button } from "@mui/material";
import { BaseUrl } from "../api/baseURL";
import sendTokenToBackend from '../api/validateToken';
import { useMsal, useIsAuthenticated } from "@azure/msal-react";

import AppBar from '@mui/material/AppBar';
import { useTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';

import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import fetchSampleQuestions from "../api/fetchQuestions";
import fetchConversationId from "../api/fetchConversationId";
import DrawerContainer from "../components/menuDrawer/drawerContainer";

// Function to create a new Timestamp object with the current time
function getCurrentTimestamp(): Timestamp {
  return {
    $date: Date.now() // Current time in milliseconds
  };
}

const updateAssistantMessage = (parentMessage: ParentMessage, newAssistantMessage: string): ParentMessage => {

  const assistantMsgIndex = parentMessage.messages.findIndex(msg => msg.role === 'assistant');

  if (assistantMsgIndex === -1) {
    console.error('No assistant message found');
    return parentMessage;
  }

  const updatedMessages = parentMessage.messages.map((msg, index) =>
    index === assistantMsgIndex ? { ...msg, message: newAssistantMessage } : msg
  );

  return {
    ...parentMessage,
    messages: updatedMessages,
  };
};


enum AppStatus {
  LoggingIn = "AUTHENTICATING",
  InitializingData = "LOADING DATA",
  GettingMessageHistory = "GETTING MESSAGE HISTORY",
  SavingConversation = "SAVING CONVERSATION",
  GeneratingChatResponse = "GENERATING CHAT RESPONSE",
  Idle = "IDLE",
  Error = "ERROR" // you can add as many statuses as needed
}


/**
 * MainPage - This component manages and renders the main page of the application.
 * It handles user login, chat functionalities, error handling, and loading states.
 */

/**
 *
 * TODO: Add APIs - figure out how to show streaming responses in chat messages
 * Add error handling/logging for error states
 * finish profile page
 * figure out what to do when 'chat' icon is clicked when already in chat menu (should probably hide icon)
 */
/**
 * The main page component that displays the header and routes to other pages.
 */
const MainPage: FC = () => {
  const { instance, accounts, inProgress } = useMsal();
  const account = accounts[0];
  const isAuthenticated = useIsAuthenticated();
  const prevUserRef = useRef<string>();
  const [isLoading, setLoading] = useState(false);
  const [appStatus, setAppStatus] = useState<AppStatus>(AppStatus.Idle);
  const [user, setUser] = useState<string | undefined>();
  const [messageHistory, setMessageHistory] = useState(Array<ParentMessage>());
  const [isError, setIsError] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<Conversation>();
  const [conversationHistory, setConversationHistory] = useState<Conversation[]>([]);
  const [apiUrl, setApiUrl] = useState<string>();
  const [sampleQuestions, setSampleQuestions] = useState<string[]>();
  const [userInput, setUserInput] = useState<string>();

  // track current values for state change
  const currentAnswerRef = useRef();
  const questionsRef = useRef<string[]>();
  const conversationHistoryRef = useRef<Conversation[]>();
  const messageRef = useRef<ParentMessage[]>();

  // event data updates
  const [streamingMessage, setStreamingMessage] = useState<string>();
  const [followups, setFollowups] = useState<Followup[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);

  console.log("loading main page")

  const theme = useTheme()

  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [isClosing, setIsClosing] = React.useState(false);
  const drawerWidth = 240;

  const handleDrawerToggle = () => {
    if (!isClosing) {
      setMobileOpen(!mobileOpen);
    }
  };

  const fetchUser = async () => {
    setUser(undefined)
    console.log(`is authenticated: ${isAuthenticated} and is inProgress: ${inProgress}`)
    if (isAuthenticated && inProgress === 'none') {

      try {

        const userData = await sendTokenToBackend(accounts[0], instance);
        console.log(`fetched user from backend ${userData}`)
        setUser(userData);

      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    }
  };


  /**
   * Resets the sample questions based on user preferences.
   * @param questionList - The list of questions to be displayed.
   */
  const getSampleQuestions = async () => {
    if (user != undefined) {
      try {
        setSampleQuestions(
          await fetchSampleQuestions({ user })
        );
      }
      catch {
        console.error("error on getting sample questions")
      }
    }
  };


  /**
   * Fetches and sets the conversation based on selected conversation.
   */
  const getConversations = async () => {
    setAppStatus(AppStatus.InitializingData)
    if (user != undefined) {
      try {
        setConversationHistory(
          await fetchConversations({
            user: user
          })
        );
      } catch (error) {
        console.error(
          `An error occurred while fetching conversations ${error}`
        );
      }
    }
  };

  const logoutUser = () => {
    console.log("logging out user: ", user);
    setUser(undefined);
    instance.logout();
  };

  /**
   * Resets the selected conversation state.
   */
  const resetConversation = () => {
    setSelectedConversation(undefined);
  };

  //change API url to match user_question
  const getChatResponse = async () => {
    if (userInput) {
    console.log(`getting chat response for ${userInput} with ${JSON.stringify(user)}, conversation id: ${JSON.stringify(selectedConversation)}`)
    let apiUrl = ''
    if (user && user != null) {
      if (selectedConversation && selectedConversation != null) {
        apiUrl = `${BaseUrl()}/users/${user}/conversations/${selectedConversation.id}/chat/${userInput}`
        setApiUrl(apiUrl)
      } else {
        console.log(`no conversation selected.  getting conversation id.`)
        setAppStatus(AppStatus.SavingConversation)
      }
    }
  }
  };

  const saveNewConversation = async () => {
    console.log(`fetching new conversation id`)
    if (user) {
      setSelectedConversation(await fetchConversationId({ user }));
  }
};

  /**
   * Fetches and sets the selected conversation.
   */
  const getSelectedConversationMessages = async () => {
    try {
      if (selectedConversation != null && user != undefined) {
        setMessageHistory(await fetchMessageHistory({
          user: user,
          conversationId: selectedConversation.id,
        }))

      }
    } catch (error) {
      console.error(`An error occurred while fetching conversations ${error}`);
    }
  };


  const runApp = () => {
    if (appStatus !== AppStatus.Idle) { setLoading(true) }
    //disable all question submit while app is processing data
    switch (appStatus) {
      case AppStatus.InitializingData:
        getConversations();
        getSampleQuestions();
        break
      case AppStatus.GettingMessageHistory:
        getSelectedConversationMessages();
        break
      case AppStatus.SavingConversation:
        saveNewConversation()
        break
      case AppStatus.GeneratingChatResponse:
        getChatResponse();
        break
      case AppStatus.LoggingIn:
        fetchUser();
        break
      case AppStatus.Idle:
        setLoading(false);
        break
      default:
        break
    }
  };

  //event detector: run app on status change event
  useEffect(() => {
    console.log(`app status updated to ${appStatus}`)
    runApp()
  }, [appStatus])

  
  //pull message history when conversation id selection changes
  //conversation changes when user selects new conversation from history list, or attemps to send a chat without any conversation saved (new chat)
  useEffect(() => {
    console.log(`selected conversation has changed.  Conversation id is ${JSON.stringify(selectedConversation)} `)
    // handle save conversation event output
    if (selectedConversation != undefined && appStatus === AppStatus.SavingConversation) { 
      console.log(`app status set back to generating chat response`)
      setAppStatus(AppStatus.GeneratingChatResponse) }

    // handle select conversation click event
    else if (selectedConversation != undefined && messageHistory !== messageRef.current) { setAppStatus(AppStatus.GettingMessageHistory) }
    else if (selectedConversation === undefined) { setMessageHistory([]) };

    return () => {
      if (appStatus !== AppStatus.GeneratingChatResponse) { setAppStatus(AppStatus.Idle) }
    }
  }, [selectedConversation]);


  //kick off user query
  useEffect(() => {
    setAppStatus(AppStatus.GeneratingChatResponse)
  }, [userInput])

  // update status and references on completion of data pulls
  useEffect(() => {
    //verify data load
    if (appStatus !== AppStatus.Idle) {
      if (conversationHistory !== undefined && sampleQuestions !== undefined) {
        // reset reference values
        if (conversationHistory !== conversationHistoryRef.current) { conversationHistoryRef.current = conversationHistory }
        if (sampleQuestions !== questionsRef.current) { questionsRef.current = sampleQuestions }
        setAppStatus(AppStatus.Idle)
      }
      if (messageHistory !== undefined && messageHistory !== messageRef.current) {
        messageRef.current = messageHistory;
        setAppStatus(AppStatus.Idle)
      }

    }
  }
    , [conversationHistory, sampleQuestions, messageHistory])

  // on user change, log in and/or reinitialize data
  useEffect(() => {
    // login
    if (user === undefined) {
      setAppStatus(AppStatus.LoggingIn)
    }
    // user changed from previous/undefined for first login
    if (user !== undefined && prevUserRef.current !== user) {
      setAppStatus(AppStatus.InitializingData)
      resetConversation()
      prevUserRef.current = user
    }

    // user logging out
    if (user === undefined && prevUserRef.current != undefined) {
      console.log("logged out.  User set to undefined");
      prevUserRef.current = undefined;
      setAppStatus(AppStatus.Idle)
      window.location.reload();
    }
  }, [, user])

  //msal event detection
  useEffect(() => {
    setAppStatus(AppStatus.LoggingIn)
  }, [accounts, instance, isAuthenticated, inProgress]); // Re-run the effect when accounts or instance changes

  // event source
  useEffect(() => {
    if (apiUrl) {

      const source = new EventSource(apiUrl);
      setLoading(true);
      source.addEventListener('message', (event) => {
        console.log(`Received raw event data: ${event.data}`)
        const data = JSON.parse(event.data);
        console.log(`recieved event data ${data}`)
        setStreamingMessage(prev => prev + data.message);
      });
      source.addEventListener('citations', (event) => {
        const data = JSON.parse(event.data);
        console.log(`recieved event data ${event.data}`)
        const newCitation: Citation = data.citations; 
        setCitations((prevCitations) => [...prevCitations, newCitation]);
      })
      source.addEventListener('followups', (event) => {
        const data = JSON.parse(event.data);
        setFollowups(event.data.split(","));
      });
      source.addEventListener('stream-ended', (event) => {
        source.close();
        setAppStatus(AppStatus.Idle);
      }
      )
      return () => {
        if (source.readyState !== EventSource.CLOSED) {
          setAppStatus(AppStatus.Idle)
          source.close();
          console.log('EventSource closed by the client.');
        }
      };
    }
  }, [apiUrl]);


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
      <DrawerContainer conversationList={conversationHistory}
       handleSelectConversation={setSelectedConversation}
        resetConversation={resetConversation}
         account={account}/>
    
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
            setConversation={setSelectedConversation}
            conversationTitle={selectedConversation?.topic}
            newChat={resetConversation}
            isError={isError}
            isLoading={isLoading}
            sampleQuestions={sampleQuestions}
            sendChatClicked={setUserInput}
            messageHistory={messageHistory}
            conversations={conversationHistory}
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
