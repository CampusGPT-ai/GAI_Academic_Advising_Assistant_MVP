import { useState, useEffect, useRef } from 'react';
import Conversation from '../model/conversation/conversations';
import fetchConversations from "../api/fetchConversations";
import fetchSampleQuestions from '../api/fetchQuestions';
import sendTokenToBackend from '../api/validateToken';
import AppStatus from "../model/conversation/statusMessages";

import { useMsal, useIsAuthenticated} from "@azure/msal-react";
import { setRef } from '@mui/material';


interface conversationHistoryStatus {
  userHasHistory: boolean,
  isHistoryUpdated: boolean,
}

interface ConversationData {
  conversations?: Conversation[];
  sampleQuestions?: string[];
  userSession?: string;
  initDataError?: string;
  conversationHistoryFlag: conversationHistoryStatus; 

}



const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';

function useAccountData(refreshFlag : Boolean, setRefreshFlag: (refreshFlag: Boolean)=>void, appStatus : AppStatus, setAppStatus: (status: AppStatus) => void, setErrorMessage?: (error: string)=>void): ConversationData {

  const { inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [userSession, setUserSession] = useState<string>();
  const [conversationHistoryFlag, setConversationHistoryFlag] = useState<conversationHistoryStatus>({userHasHistory: true, 
    isHistoryUpdated: false});
  const [sampleQuestions, setSampleQuestions] = useState<string[]>();
  const [conversations, setConversations] = useState<Conversation[]>();
  const priorStatus = useRef<AppStatus>(AppStatus.Idle);
  const sessionRef = useRef<string>();
  const conversationRef = useRef<Conversation[]>();
  const refreshRef = useRef<Boolean>();

  const { instance, accounts } = useMsal();

  
  /**
   * Fetches user data from the backend and updates the user session.
   * Sets the app status to LoggingIn while fetching the user data.
   * If successful, sets the app status to Idle and updates the user session.
   * If there is an error, sets the app status to Error and sets the error message.
   */
  const fetchUser = async () => {
    setAppStatus(AppStatus.LoggingIn)
    priorStatus.current = AppStatus.LoggingIn;
    console.log(`fetching user from backend`)
      try {
        const userData = await sendTokenToBackend({accounts, isAuthenticated, inProgress, instance});
        console.log(`fetched user from backend ${userData}`)
        setUserSession(userData);
      } catch (error) {
        setAppStatus(AppStatus.Error)
        console.error(`Error fetching user token: ${error}`);
        setErrorMessage && setErrorMessage(`Error fetching user token: ${error}`);
      }
  };

  const getSampleQuestions = async () => {
    setSampleQuestions(undefined);
    setAppStatus(AppStatus.GettingQuestions)
      try {
        setSampleQuestions(
          await fetchSampleQuestions({user: userSession})
        );
      }
      catch (error) {
        setAppStatus(AppStatus.Error)
        setErrorMessage && setErrorMessage(`Error fetching sample questions: ${error}`);
      }
  };

  const getConversations = async () => {
    appStatus !== AppStatus.GeneratingChatResponse && setAppStatus(AppStatus.GettingConversations)
    console.log(`fetching conversations for user: ${userSession}`)
      try {
        const result = await fetchConversations({
          user: userSession
        })
        // history flag works if history is updated
        // console.log(`result from fetchConversations: ${JSON.stringify(result)}`)
        result.message==='no history found' && setConversationHistoryFlag({userHasHistory: false, isHistoryUpdated: false})
        result.data && setConversations(result.data);
        conversationRef.current = result.data;
        result.data && setConversationHistoryFlag({userHasHistory: true, isHistoryUpdated: true})
      } catch (error) {
        setAppStatus(AppStatus.Error)
        setErrorMessage && setErrorMessage(`Error fetching conversation history: ${error}`);
    }
  };

  useEffect(() => {
    if (refreshFlag !== refreshRef.current) {
      refreshRef.current = refreshFlag;
    // if a new conversation has been added, refresh the history list
    console.log(`conversation refresh flag change detected ${refreshFlag}`)
    refreshFlag && userSession &&
    getConversations();
    setRefreshFlag(false);
    }
},[refreshFlag])

  useEffect(() => {
    if (userSession != undefined && sessionRef.current !== userSession) {
      console.log(`user session updated to ${userSession}.  Refreshing conversation and questions`)
      sessionRef.current = userSession;
      !(appStatus === AppStatus.Error) && getConversations();
      !(appStatus === AppStatus.Error) && getSampleQuestions();
    }
  }, [userSession, appStatus]);

  useEffect(() => {
    if ((conversations || !conversationHistoryFlag.userHasHistory) && sampleQuestions) {
      console.log(`conversations and questions updated.  Setting app status to idle`);
      (appStatus === AppStatus.GettingConversations || appStatus === AppStatus.GettingQuestions) && setAppStatus(AppStatus.Idle);
    }
  }, [conversations, sampleQuestions, conversationHistoryFlag, appStatus])

  useEffect(() => {
    // retrieve token with user id from backend
    // .log(`fetching session data for Auth type: ${AUTH_TYPE}`)

    !userSession && appStatus === AppStatus.Idle && fetchUser();

  }, [isAuthenticated, inProgress, AUTH_TYPE, userSession, appStatus]
  )


  return { userSession, sampleQuestions, conversations, conversationHistoryFlag};
}

 export default useAccountData;