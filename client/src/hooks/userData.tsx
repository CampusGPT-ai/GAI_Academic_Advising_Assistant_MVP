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

function useAccountData(refreshFlag : Boolean, setRefreshFlag: (refreshFlag: Boolean)=>void, setAppStatus: (status: AppStatus) => void): ConversationData {

  const { inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [userSession, setUserSession] = useState<string>();
  const [conversationHistoryFlag, setConversationHistoryFlag] = useState<conversationHistoryStatus>({userHasHistory: true, 
    isHistoryUpdated: false});
  const [sampleQuestions, setSampleQuestions] = useState<string[]>();
  const [conversations, setConversations] = useState<Conversation[]>();
  const [initDataError, setInitDataError] = useState<string>();
  const priorStatus = useRef<AppStatus>(AppStatus.Idle);
  const sessionRef = useRef<string>();
  const conversationRef = useRef<Conversation[]>();


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
    // console.log(`fetching user from backend`)
      try {
        const userData = await sendTokenToBackend({accounts, isAuthenticated, inProgress, instance});
        // console.log(`fetched user from backend ${userData}`)
        setUserSession(userData);
      } catch (error) {
        setAppStatus(AppStatus.Error)
        setInitDataError(`Error fetching user token: ${error}`);
      }
  };

  const getSampleQuestions = async () => {
    setAppStatus(AppStatus.GettingQuestions)
      try {
        setSampleQuestions(
          await fetchSampleQuestions({user: userSession})
        );
      }
      catch (error) {
        setAppStatus(AppStatus.Error)
        setInitDataError(`Error fetching sample questions: ${error}`);
      }
  };

  const getConversations = async () => {
    setAppStatus(AppStatus.GettingConversations)
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
        setInitDataError(`Error fetching conversation history: ${error}`);
    }
  };

  useEffect(() => {
    // if a new conversation has been added, refresh the history list
    console.log(`conversation refresh flag change detected ${refreshFlag}`)
    refreshFlag && userSession &&
    getConversations();
    setRefreshFlag(false);
},[refreshFlag])

  useEffect(() => {
    if (userSession != undefined && sessionRef.current !== userSession) {
      sessionRef.current = userSession;
      getConversations();
      getSampleQuestions();
    }
  }, [userSession]);

  useEffect(() => {
    if ((conversations || !conversationHistoryFlag.userHasHistory) && sampleQuestions) {
      setAppStatus(AppStatus.Idle);
    }
  }, [conversations, sampleQuestions, conversationHistoryFlag])

  useEffect(() => {
    // retrieve token with user id from backend
    // .log(`fetching session data for Auth type: ${AUTH_TYPE}`)
    !userSession && fetchUser();
  }, [isAuthenticated, inProgress, AUTH_TYPE, userSession]
  )


  return { userSession, sampleQuestions, conversations, initDataError, conversationHistoryFlag};
}

 export default useAccountData;