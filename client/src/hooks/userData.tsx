import { useState, useEffect, useRef } from 'react';
import Conversation from '../model/conversation/conversations';
import fetchConversations from "../api/fetchConversations";
import fetchSampleQuestions from '../api/fetchQuestions';
import sendTokenToBackend from '../api/validateToken';
import AppStatus from "../model/conversation/statusMessages";

import { useMsal, useIsAuthenticated} from "@azure/msal-react";



interface detectHistoryRefresh {
  isNewConversation: boolean,
  isMessageLoaded: boolean,
}

interface conversationHistoryStatus {
  userHasHistory: boolean,
  isHistoryUpdated: boolean,
}

interface ConversationData {
  conversations?: Conversation[];
  sampleQuestions?: string[];
  userSession?: string;
  initDataError?: string;
  dataStatus: AppStatus;
  conversationHistoryFlag: conversationHistoryStatus; 

}

interface AccountData {
    refreshFlag: detectHistoryRefresh;
    
}

const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';

function useAccountData({refreshFlag }: AccountData): ConversationData {

  const { inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [userSession, setUserSession] = useState<string>();
  const [conversationHistoryFlag, setConversationHistoryFlag] = useState<conversationHistoryStatus>({userHasHistory: true, 
    isHistoryUpdated: false});
  const [sampleQuestions, setSampleQuestions] = useState<string[]>();
  const [conversations, setConversations] = useState<Conversation[]>();
  const [initDataError, setInitDataError] = useState<string>();
  const [appStatus, setAppStatus] = useState<AppStatus>(AppStatus.Idle);

  const fetchUser = async () => {
    setAppStatus(AppStatus.LoggingIn)
    console.log(`fetching user from backend`)
    debugger;
      try {
        const userData = await sendTokenToBackend();
        //console.log(`fetched user from backend ${userData}`)
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
        result.message==='info' && setConversationHistoryFlag({userHasHistory: false, isHistoryUpdated: false})
        result.data && setConversations(result.data);
        result.data && setConversationHistoryFlag({userHasHistory: true, isHistoryUpdated: true})
      } catch (error) {
        setAppStatus(AppStatus.Error)
        setInitDataError(`Error fetching conversation history: ${error}`);
    }
  };

  useEffect(() => {
    // if a new conversation has been added, refresh the history list
    refreshFlag.isMessageLoaded && refreshFlag.isNewConversation && userSession &&
    getConversations();
    // otherwise, set the refresh flag to false (no new history item) and return the history flag update status to false (no new updates)
    !refreshFlag.isMessageLoaded &&!refreshFlag.isNewConversation && setConversationHistoryFlag({userHasHistory: true, isHistoryUpdated: false})
  },[refreshFlag])

  useEffect(() => {
    if (userSession != undefined) {
        getConversations();
        getSampleQuestions();
    }
  }, [userSession]);

  useEffect(() => {
    if (conversations && sampleQuestions) {
      setAppStatus(AppStatus.Idle);
    }
  }, [conversations, sampleQuestions])

  useEffect(() => {
    // retrieve token with user id from backend
    console.log(`fetching session data for Auth type: ${AUTH_TYPE}`)
    !userSession && fetchUser();

  }, [isAuthenticated, inProgress, AUTH_TYPE, userSession]
  )

  return { userSession, sampleQuestions, conversations, initDataError, dataStatus: appStatus, conversationHistoryFlag};
}

 export default useAccountData;