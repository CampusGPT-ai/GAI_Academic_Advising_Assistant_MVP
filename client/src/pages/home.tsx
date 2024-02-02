//src/components/pages/index.tsxfetchmessages

import React, { FC, useEffect, useRef, useState } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import fetchChatResponse from "../api/fetchChatResponse";
import fetchConversations from "../api/fetchConversations";
import fetchMessageHistory from "../api/fetchMessages";
import fetchTopics from "../api/fetchTopics";
import Conversation from "../model/conversation/conversations";
import Message, { Citation } from "../model/messages/messages";
import { Topic } from "../model/topic/topics";
import { UserProfile } from "../model/user/user";
import getUserProfile from "../utilities/getDemoProfile";
import { getFirstThreeQuestions } from "../utilities/parseTopics";
import Footer from "../components/footer/footer";
import Header from "../components/header/header";
import Chat from "./chat";
import { Box } from "@mui/material";

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
  const [sampleQuestions, setSampleQuestions] = useState([""]);
  const [title, setTitle] = useState("YOUR PERSONAL CAMPUS GUIDE"); //pull from institutions? this is the header bar title - for example: FSU
  const [user, setUser] = useState<UserProfile>();
  const [loggedIn, setLoggedIn] = useState(false);
  const [messageHistory, setMessageHistory] = useState(Array<Message>());
  const [error, setError] = useState("");
  const [isError, setIsError] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<Conversation>();
  const [conversationHistory, setConversationHistory] = useState<Conversation[]>([]);

  const currentAnswerRef = useRef(null);
  const [topicList, setTopicList] = useState<string[]>();

  // workaround for being able to access state in event listener
  const [streamingMessage, _setStreamingMessage] = useState<Message>();
  const streamingMessageRef = useRef(streamingMessage);
  const setStreamingMessage = (data?: Message) => {
    streamingMessageRef.current = data;
    _setStreamingMessage(data);
  };
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

  /**
   * Fetches and sets the topics/questions to be displayed in the example chat based on database.
   * Always runs once on first load based on useEffect empty dependency array[].
   */
  //TODO: update to pull topics from get topics api vs. sample data for demo app
  const getTopics = async () => {
    try {
      setTopicList(await fetchTopics({}));
    } catch (error) {
      console.error(
        "An error occurred while getting sample questions: ",
        error
      );
    }
  };


  const onChatResponseStreamOpen = () => {
    let message = {
      role: "bot",
      message: ""
    }
    console.log("streaming response open, set streaming message");
    setStreamingMessage(message);
  }


  const onChatResponseStreamUpdate = (newResponse: string, isFirstChunk: boolean) => {
    console.log(`got response chunk: ${newResponse}`)
    if (isFirstChunk) {
      setLoading(prevLoading => !prevLoading);
      if (currentAnswerRef && currentAnswerRef.current) {
        let el = currentAnswerRef.current as HTMLElement;
        el.innerHTML += newResponse;
      }
    }
    else {
      if (currentAnswerRef && currentAnswerRef.current) {
        let el = currentAnswerRef.current as HTMLElement;
        el.innerHTML = newResponse;
      }
    }
  }


  const onChatResponseMetaDataUpdate = (metaData: any, message: string) => {
    console.log(`Updating response metadata: ${metaData}`)
    let convo = JSON.parse(metaData.conversation)
    let convoParsed = {
      id: convo.id,
      topic: convo.topic,
      start_time: convo.start_time ? convo.start_time.$date : 0,
      end_time: convo.end_time ? convo.end_time.$date : 0,
    } as Conversation;

    // convert citations to client format
    //let citations = metaData.citations.map((x: any) => ({ CitationText: x.citation_text, CitationPath: x.citation_path }));
    let citations = [] as Citation[];
    for (var i in metaData.citations) {
      let cit = JSON.parse(metaData.citations[i]);
      citations.push({ CitationText: cit.citation_text, CitationPath: cit.citation_path });
    }
    // replace citations with inline superscript
    for (let i in citations) {
      let cit = citations[i];
      console.log("replacing citation: ", cit.CitationText);
      message = message.replaceAll("[" + cit.CitationText + "]", `<sup>${Number(i)+1}</sup>`);
    }

    //create the new message object and add it to state
    let messageObj = {
      role: "bot",
      message: message,
      topic: convoParsed.topic,
      Citations: citations,
      Followups: metaData.followups.map( (x: string) => ({ FollowupQuestion: x }) )
    } as Message;
    
    setStreamingMessage(messageObj);
    console.log("received conversation " + convoParsed.id + " with topic " + convoParsed.topic)
    setSelectedConversation(convoParsed)
  }

  const onChatResponseStreamDone = () => {
    console.log("streaming response done");
    if (streamingMessageRef.current) {
      let newMessage = streamingMessageRef.current;
      console.log("streaming response done: setting streaming message in history");
      setMessageHistory((prevMessages: Message[]) => [...prevMessages, newMessage]);
    }
    setStreamingMessage(undefined);
    setLoading(false);
  }
  
  const onStreamingError = (error: Error) => {
    setIsError(prevError => !prevError);
    console.error(`error message recieved from streaming chat ${error}`);
    setError(error.message);

  }

  /**
   * Fetches the chat response and updates the messages state.
   * @param messageText - The text message from the user.
   */
  const getChatResponse = async (messageText: string) => {
    console.log("fetching chat response start")
    setLoading(prevLoading => !prevLoading);
    let userMessage = { role: "user", message: messageText }
    setMessageHistory((prevMessages: Message[]) => [...prevMessages, userMessage]);
    try {
      // this will need to be changed to work with streaming response
      let user_id = user ? user.user_id : undefined;
      
      let conversation_id = selectedConversation ? selectedConversation._id : "null";
      await fetchChatResponse({ messageText, conversation_id, user_id },
        onChatResponseStreamUpdate,
        onChatResponseMetaDataUpdate,
        onChatResponseStreamDone,
        onChatResponseStreamOpen,
        onStreamingError,
      );

    } catch (error) {
      console.error(error)
    }

   
  };

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
        setMessageHistory(
          await fetchMessageHistory({
            user: user.user_id,
            conversationId: conversation,
          })
        );
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

  useEffect(() => {
    getTopics();
    console.log("getting sample questions");

    const sessionUser = sessionStorage.getItem("user");
    if (sessionUser) {
      try {
        const user: UserProfile = JSON.parse(sessionUser); // Parse it to an object
        setUser(user); // Set the user state
      } catch (error) {
        console.error("An error occurred while parsing the user: ", error);
      }
    }
  }, []);

  useEffect(() => {
    console.log(`messages updated to: ${JSON.stringify(messageHistory)}`);
  }, [messageHistory]);

  useEffect(() => {
    //topicList && console.log(`Got topics: ${JSON.stringify(topicList)}`)
    topicList && setSampleQuestions(topicList.slice(0,3));
  }, [topicList]);

  useEffect(() => {
    sampleQuestions &&
      console.log("sample questions updated to: ", sampleQuestions);
  }, [sampleQuestions]);

  useEffect(() => {
    console.log(`loading state change detected: ${isLoading}`)
  },[isLoading])
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
            />


      <Footer></Footer>
    </Box>
  );
};

export default MainPage;
