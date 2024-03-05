import { useState, useEffect, useRef } from 'react';
import Conversation from '../model/conversation/conversations';
import fetchConversations from "../api/fetchConversations";
import fetchSampleQuestions from '../api/fetchQuestions';
import sendTokenToBackend from '../api/validateToken';
import AppStatus from "../model/conversation/statusMessages";
import { Apps } from '@mui/icons-material';

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
  conversationHistoryFlag: conversationHistoryStatus; 

}

interface AccountData {
    accounts: any;
    instance: any;
    isAuthenticated: any;
    inProgress: any;
    refreshFlag: detectHistoryRefresh;
    setAppStatus: (status: AppStatus) => void;
    
}

function useAccountData({accounts, instance, isAuthenticated, inProgress, refreshFlag, setAppStatus }: AccountData): ConversationData {
  const [userSession, setUserSession] = useState<string>();
  const [conversationHistoryFlag, setConversationHistoryFlag] = useState<conversationHistoryStatus>({userHasHistory: true, 
    isHistoryUpdated: false});
  const [sampleQuestions, setSampleQuestions] = useState<string[]>();
  const [conversations, setConversations] = useState<Conversation[]>();
  const [initDataError, setInitDataError] = useState<string>();

  const fetchUser = async () => {
    setAppStatus(AppStatus.LoggingIn)
      try {
        const userData = await sendTokenToBackend(accounts[0], instance);
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
      finally {
        setAppStatus(AppStatus.Idle);
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
    finally {
      setAppStatus(AppStatus.Idle);
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
    //if (isAuthenticated && inProgress === 'none') {
    if (inProgress === 'none') {
    fetchUser();
    }
  }, [isAuthenticated, inProgress]
  )

  return { userSession, sampleQuestions, conversations, initDataError, conversationHistoryFlag};
}

 export default useAccountData;
