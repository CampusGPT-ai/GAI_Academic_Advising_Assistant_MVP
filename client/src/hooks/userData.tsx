import { useState, useEffect, useRef } from 'react';
import Conversation from '../model/conversation/conversations';
import fetchConversations from "../api/fetchConversations";
import fetchSampleQuestions from '../api/fetchQuestions';
import sendTokenToBackend from '../api/validateToken';
import AppStatus from "../model/conversation/statusMessages";

import { useMsal, useIsAuthenticated} from "@azure/msal-react";


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

interface AccountData {
    newConversationFlag: Boolean;
    setAppStatus: (status: AppStatus) => void;
    
}

const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';

function useAccountData({newConversationFlag, setAppStatus }: AccountData): ConversationData {

  const { inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [userSession, setUserSession] = useState<string>();
  const [conversationHistoryFlag, setConversationHistoryFlag] = useState<conversationHistoryStatus>({userHasHistory: true, 
    isHistoryUpdated: false});
  const [sampleQuestions, setSampleQuestions] = useState<string[]>();
  const [conversations, setConversations] = useState<Conversation[]>();
  const [initDataError, setInitDataError] = useState<string>();


    const { instance, accounts } = useMsal();


  const fetchUser = async () => {
    setAppStatus(AppStatus.LoggingIn)
    console.log(`fetching user from backend`)
      try {
        const userData = await sendTokenToBackend({accounts, isAuthenticated, inProgress, instance});
        console.log(`fetched user from backend ${userData}`)
        setUserSession(userData);
        setAppStatus(AppStatus.Idle)
      } catch (error) {
        setAppStatus(AppStatus.Error)
        setInitDataError(`Error fetching user token: ${error}`);
      }
  };

  const getSampleQuestions = async () => {
    setAppStatus(AppStatus.InitializingData)
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
    setAppStatus(AppStatus.InitializingData)
      try {
        const result = await fetchConversations({
          user: userSession
        })
        // history flag works if history is updated
        console.log(`result from fetchConversations: ${JSON.stringify(result)}`)
        result.message==='no history found' && setConversationHistoryFlag({userHasHistory: false, isHistoryUpdated: false})
        result.data && setConversations(result.data);
        result.data && setConversationHistoryFlag({userHasHistory: true, isHistoryUpdated: true})
      } catch (error) {
        setAppStatus(AppStatus.Error)
        setInitDataError(`Error fetching conversation history: ${error}`);
    }
  };

  useEffect(() => {
    // if a new conversation has been added, refresh the history list
    newConversationFlag && userSession &&
    getConversations();
},[newConversationFlag])

  useEffect(() => {
    if (userSession != undefined) {
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
    console.log(`fetching session data for Auth type: ${AUTH_TYPE}`)
    !userSession && fetchUser();

  }, [isAuthenticated, inProgress, AUTH_TYPE, userSession]
  )

  useEffect(() => {
    console.log(`conversation history flag is ${JSON.stringify(conversationHistoryFlag)}`)
  }, [conversationHistoryFlag])

  return { userSession, sampleQuestions, conversations, initDataError, conversationHistoryFlag};
}

 export default useAccountData;