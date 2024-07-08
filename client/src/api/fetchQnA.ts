import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { BaseUrl } from "./baseURL";
import { ConversationNew } from '../model/conversation/conversations';
import { MessageSimple } from '../model/messages/messages';
import AppStatus from '../model/conversation/statusMessages';
// Define TypeScript interfaces for the expected data structure
interface ConversationReference {
    topic: string;
    id: string;
    start_time: any;
    end_time: any | null;
}

interface KickbackResponse {
    response: string;
    search_query: string;
    consideration_to_follow_up_on: string;
    follow_up_question: string;
}

interface RagResponse {
    topic: string;
    response: string;
}

interface ApiData {
    conversation_reference: ConversationReference;
    kickback_response: KickbackResponse;
    rag_response: RagResponse;
}

const useQnAData = (
    messageText?: string, 
    user_id?: string, 
    conversation_id?: string, 
    setUserQuestion?: (question: string) => void,
    setSelectedConversation?: (conversation: ConversationNew) => void, 
    updateHistory?: (userMessage: MessageSimple) => void, 
    setAppStatus?: (appStatus: AppStatus) => void,
    setIsError?: (isError: boolean) => void,
    setErrorMessage?: (error: string) => void,
    setRefreshFlag?: (refreshFlag: boolean) => void,
    setTriggerFetch?: (triggerFetch: boolean) => void
    ) => {
    const [conversationReference, setConversationReference] = useState<ConversationReference | null>(null);
    const [kickbackResponse, setKickbackResponse] = useState<KickbackResponse | null>(null);
    const [noKickback, setNoKickback] = useState<boolean>(false); // [NEW
    const [ragResponse, setRagResponse] = useState<RagResponse | null>(null);
    const [apiUrl, setApiUrl] = useState<string>('');
    const conversationRef = useRef<string | null>(null);

    const fetchData = async () => {
        try {
            setAppStatus && setAppStatus(AppStatus.GeneratingChatResponse);

            const response = await axios.get<ApiData>(apiUrl);
            const data = response.data;

            // Update state variables with the data from the API
            setRagResponse(data.rag_response);
            !data.kickback_response && setNoKickback(true); 
            setKickbackResponse(data.kickback_response);
            setConversationReference(data.conversation_reference);

            // console.log('Data fetched:', JSON.stringify(data));
        } catch (error: any) {
            if (axios.isAxiosError(error)) {
              console.error('API error:', error.response?.status, error.response?.data);
              if (error.response?.status === 401) {
                setIsError && setIsError(true);
                setErrorMessage && setErrorMessage('Unauthorized'); // Specific handling for 401 error
              } else {
                // Optional: Handle other specific status codes if necessary
                console.error('Unhandled API error', error.response?.status);
                setIsError && setIsError(true);
                setErrorMessage && setErrorMessage('Error fetching messages');
              }
            } else {
              // Non-Axios error
              console.error('Error:', error.message);
              setIsError && setIsError(true);
              setErrorMessage && setErrorMessage('An unexplained error occurred');
            }
          }
        };
     
    const resetStatus = () => {
        setApiUrl('');
        setAppStatus && setAppStatus(AppStatus.Idle);
        setKickbackResponse(null);
        setRagResponse(null);
        setNoKickback(false);
        setUserQuestion && setUserQuestion('');
        setTriggerFetch && setTriggerFetch(true);
    };


    useEffect(() => {
        if (messageText) {
            // console.log('useQnAData useEffect triggered')
                
                if (user_id) {
                    const safeMessageText = messageText.replace(/\//g, '-');
                    const encodedMessageText = encodeURIComponent(safeMessageText);
                    if (conversation_id) {
                        setApiUrl(`${BaseUrl()}/users/${user_id}/conversations/${conversation_id}/chat_new/${encodedMessageText}`)
                    } else {
                        setApiUrl(`${BaseUrl()}/users/${user_id}/conversations/0/chat_new/${encodedMessageText}`)
                    }
                }
            }
    }, [messageText, conversation_id, user_id]);

    useEffect(() => {
        if (apiUrl) {
            // console.log('Fetching data...');
            try {
                fetchData();
            }
            catch (error) {
                console.error('Error fetching data for user question:', error);
                setAppStatus && setAppStatus(AppStatus.Error);
            }
            
        }
    }, [apiUrl]);

    useEffect(() => {
        if (setSelectedConversation && conversationReference) {
            // trigger refresh of conversation history list
            //
            // console.log(`setting refresh flag with conversation reference conversationReference: ${JSON.stringify(conversationReference)} and conversationRef.current: ${conversationRef.current}`)
            setRefreshFlag && setRefreshFlag(true);
            conversationRef.current = conversationReference.id;
            const conversation: ConversationNew = { id: conversationReference.id, topic: conversationReference.topic, start_time: conversationReference.start_time };
            setSelectedConversation(conversation);
        }
        //change
    }, [conversationReference])// Dependency array, the effect runs when the URL changes


    useEffect(() => {

        if (updateHistory && ragResponse) {
            // console.log(`ragResponse: ${ragResponse.response}`)
            const ru: MessageSimple = { role: "system", message: ragResponse.response, created_at: { $date: Date.now() } };
            updateHistory && updateHistory(ru);
        }
        if (updateHistory && kickbackResponse) {
            // console.log(`kickbackResponse: ${kickbackResponse.follow_up_question}`)
            const followUpQuestion: MessageSimple = { role: "system", message: kickbackResponse.follow_up_question, created_at: { $date: Date.now() } };
            updateHistory && updateHistory(followUpQuestion);
        }

        if (ragResponse && (kickbackResponse || noKickback)) {
         resetStatus();
        }

    }, [kickbackResponse, ragResponse])

    return { isNewConversation: conversationReference?.id !== conversationRef.current};
};

export default useQnAData;
