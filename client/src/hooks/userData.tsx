import { useState, useEffect, useRef } from 'react';
import Conversation from '../model/conversation/conversations';
import fetchConversations from "../api/fetchConversations";
import fetchSampleQuestions from '../api/fetchQuestions';
import sendTokenToBackend from '../api/validateToken';
import AppStatus from "../model/conversation/statusMessages";

interface ConversationData {
  conversations?: Conversation[];
  sampleQuestions?: string[];
  userSession?: string;
  initDataError?: string;
  dataStatus: AppStatus;
}

interface AccountData {
    accounts: any;
    instance: any;
    isAuthenticated: any;
    inProgress: any;
    
}

function useAccountData({accounts, instance, isAuthenticated, inProgress }: AccountData): ConversationData {
  const [userSession, setUserSession] = useState<string>();
  const [sampleQuestions, setSampleQuestions] = useState<string[]>();
  const [conversations, setConversations] = useState<Conversation[]>();
  const [initDataError, setInitDataError] = useState<string>();
  const appStatus = useRef<AppStatus>(AppStatus.Idle);

  const fetchUser = async () => {
    appStatus.current = AppStatus.LoggingIn
      try {
        const userData = await sendTokenToBackend(accounts[0], instance);
        //console.log(`fetched user from backend ${userData}`)
        setUserSession(userData);
      } catch (error) {
        setInitDataError(`Error fetching user token: ${error}`);
      }
  };

  const getSampleQuestions = async () => {
    appStatus.current = AppStatus.InitializingData
      try {
        setSampleQuestions(
          await fetchSampleQuestions({user: userSession})
        );
      }
      catch (error) {
        setInitDataError(`Error fetching sample questions: ${error}`);
      }
    
  };

  const getConversations = async () => {
    appStatus.current = AppStatus.InitializingData
      try {
        setConversations(
          await fetchConversations({
            user: userSession
          })
        );
      } catch (error) {
        setInitDataError(`Error fetching conversation history: ${error}`);
      
    }
  };

  useEffect(() => {
    if (userSession != undefined) {
        getConversations();
        getSampleQuestions();
    }
  }, [userSession]);

  useEffect(() => {
    if (conversations && sampleQuestions) {
    appStatus.current = AppStatus.Idle;
    }
  })

  useEffect(() => {
    // retrieve token with user id from backend
    if (isAuthenticated && inProgress === 'none') {
    fetchUser();
    }
  }, [isAuthenticated, inProgress]
  )

  return { userSession, sampleQuestions, conversations, initDataError, dataStatus: appStatus.current};
}

 export default useAccountData;