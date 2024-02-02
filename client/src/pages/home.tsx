//src/components/pages/index.tsxfetchmessages

import React, { FC, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import fetchChatResponse from "../api/fetchChatResponse";
import fetchConversations from "../api/fetchConversations";
import fetchMessageHistory from "../api/fetchMessages";
import Conversation from "../model/conversation/conversations";
import ParentMessage, { Message, Citation, Timestamp, Followup } from "../model/messages/messages";
import { UserProfile } from "../model/user/user";
import getUserProfile from "../utilities/getDemoProfile";
import Footer from "../components/footer/footer";
import Header from "../components/header/header";
import Chat from "./chat";
import { Box } from "@mui/material";
import { BaseUrl } from "../api/baseURL";

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
  const navigate = useNavigate();
  const prevUserRef = useRef<UserProfile>();
  const [isLoading, setLoading] = useState(false);
  const [title, setTitle] = useState("YOUR PERSONAL CAMPUS GUIDE"); //pull from institutions? this is the header bar title - for example: FSU
  const [user, setUser] = useState<UserProfile>();
  const [loggedIn, setLoggedIn] = useState(false);
  const [messageHistory, setMessageHistory] = useState(Array<ParentMessage>());
  const [error, setError] = useState("");
  const [isError, setIsError] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<Conversation>();
  const [conversationHistory, setConversationHistory] = useState<Conversation[]>([]);
  const [apiUrl, setApiUrl] = useState<string>();
  const [sourceOpen, setSourceOpen] = useState<boolean>(false);
  const currentAnswerRef = useRef(null);

 // event data updates
  const [streamingMessage, setStreamingMessage] = useState<string>();
  const [sampleQuestions, setSampleQuestions] = useState<string[]>(['none provided']);
  const [followups, setFollowups] = useState<Followup[]>();
  const [citations, setCitations] = useState<Citation[]>();

  console.log("loading main page")

  /**
   * Handles the profile button click event and navigates to the login page.
   */
  const profileButtonClicked = () => {
    console.log("profile button clicked");
    navigate("login");
  };

  /**
   * Resets the sample questions based on user preferences.
   * @param questionList - The list of questions to be displayed.
   */
  const getSampleQuestions = (questionList: string[]) => {
    setSampleQuestions(questionList);
  };

  /**
   * Fetches and sets the user data based on the user_id and loads chat page.
   * @param user_id - The ID of the user.
   */
  //TODO: update to get user from db vs. dummy profile for demo app
  const getUser = async (user_id: string) => {
    try {
      const user: UserProfile = getUserProfile(user_id);
      setUser(user);
      sessionStorage.setItem("user", JSON.stringify(user));
    } catch (error) {
      console.error(`An error occurred while getting user profile: ${error}`);
    }
  };

  //TODO: Add logging to see what the data looks like when it comes in.  
  useEffect(() => {
    if (apiUrl)  {
       
      const source = new EventSource(apiUrl);
      setSourceOpen(true);
      source.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        console.log(`recieved event data ${event.data}`)
        setStreamingMessage(prev => prev + data.message);
      });
      source.addEventListener('citations', (event) => {
        const data = JSON.parse(event.data);
        console.log(`recieved event data ${event.data}`)
        const citations : string = data.citations;
      })
      source.addEventListener('followups', (event) => {
        const data = JSON.parse(event.data);
        console.log(`recieved event data ${event.data}`)
      });
      source.addEventListener('stream-ended', (event) =>
        source.close()
      )
      return () => {
        if (source.readyState !== EventSource.CLOSED) {
          source.close();
          setSourceOpen(false);
          console.log('EventSource closed by the client.');
        }
      };
    }
  }, [apiUrl]);

  /**
   * Fetches and sets the conversation based on selected conversation.
   */
  const getConversations = async () => {
    if (user?.user_id != undefined && user?.institution != undefined) {
      try {
        setConversationHistory(
          await fetchConversations({
            user: user.user_id,
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
    console.log("logging out user: ", user?.full_name);
    sessionStorage.removeItem("user");
    setUser(undefined);
  };

  /**
   * Resets the selected conversation state.
   */
  const resetConversation = () => {
    setSelectedConversation(undefined);
  };

  const getChatResponse = (user_question: string) => {
    setApiUrl
  };

  /**
   * Fetches and sets the selected conversation.
   */
  const getSelectedConversationMessages = async (conversation: string) => {
    try {
      if (
        conversation != null &&
        user?.user_id != undefined &&
        user?.institution != undefined
      ) {
      const chatMessages = await fetchMessageHistory({
            user: user.user_id,
            conversationId: conversation,
          })
        
      }
    } catch (error) {
      console.error(`An error occurred while fetching conversations ${error}`);
    }
  };

  useEffect(() => {
    console.log(`selected conversation has changed.  Conversation id is ${JSON.stringify(selectedConversation)} `)
    selectedConversation != undefined &&
      getSelectedConversationMessages(selectedConversation.id);
    selectedConversation === undefined && setMessageHistory([]);
  }, [selectedConversation]);

  //** On user change effects: get new conversation history, update previous user reference, set loggedin flags.
  useEffect(() => {
    if (user != undefined) {
      if (prevUserRef.current === undefined || prevUserRef.current != user) {
        resetConversation();
        getConversations();
        prevUserRef.current = user;
        setLoggedIn(true);
        navigate("chat");
      }
    }

    if (user === undefined && prevUserRef.current != undefined) {
      console.log("logged out.  User set to undefined");
      prevUserRef.current = undefined;
      setLoggedIn(false);
      window.location.reload();
    }
  }, [user]);

  return (
    <Box sx={{backgroundColor: (theme) => theme.palette.primary.main}}>
      <Header //src/sections/header.tsx
        title={title}
        handleLogout={logoutUser}
        loggedIn={loggedIn}
        profileButtonClicked={profileButtonClicked}
        setSampleQuestions={getSampleQuestions} //this should change the questions visible in the chat pane
        user={user}
      />

            <Chat
              setConversation={setSelectedConversation}
              conversationTitle={selectedConversation?.topic}
              newChat={resetConversation}
              error={error}
              isError={isError}
              isLoading={isLoading}
              sampleQuestions={sampleQuestions}
              isLoggedIn={loggedIn}
              sendChatClicked={getChatResponse}
              messageHistory={messageHistory}
              conversations={conversationHistory}
              chatResponse={streamingMessage}
              currentAnswerRef={currentAnswerRef}
              follow_up_questions={followups}
              citations={citations}
              sourceOpen={sourceOpen}
            />


      <Footer></Footer>
    </Box>
  );
};

export default MainPage;
