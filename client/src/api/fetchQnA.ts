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
    setSelectedConversation?: (conversation: ConversationNew) => void, 
    updateHistory?: (userMessage: MessageSimple) => void, 
    setAppStatus?: (appStatus: AppStatus) => void,
    setIsError?: (isError: boolean) => void,
    setErrorMessage?: (error: string) => void,
    setRefreshFlag?: (refreshFlag: boolean) => void
    ) => {
    const [conversationReference, setConversationReference] = useState<ConversationReference | null>(null);
    const [kickbackResponse, setKickbackResponse] = useState<KickbackResponse | null>(null);
    const [noKickback, setNoKickback] = useState<boolean>(false); // [NEW
    const [ragResponse, setRagResponse] = useState<RagResponse | null>(null);
    const [apiUrl, setApiUrl] = useState<string>('');
    const apiUrlRef = useRef<string | null>(null);
    const conversationRef = useRef<string | null>(null);
    const userQuestionRef = useRef<string | null>(null);
    const ragRef = useRef<string | null>(null);
    const kickbackRef = useRef<string | null>(null);

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

            console.log('Data fetched:', JSON.stringify(data));
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


    useEffect(() => {
        if (messageText) {
            if (userQuestionRef.current === messageText) {
                return;
            }
            else {
                
                if (user_id) {
                    const safeMessageText = messageText.replace(/\//g, '-');
                    const encodedMessageText = encodeURIComponent(safeMessageText);
                    if (conversation_id) {
                        setApiUrl(`${BaseUrl()}/users/${user_id}/conversations/${conversation_id}/chat_new/${encodedMessageText}`)
                    } else {
                        setApiUrl(`${BaseUrl()}/users/${user_id}/conversations/0/chat_new/${encodedMessageText}`)
                    }
                }

                userQuestionRef.current = messageText;
            }
        }
    }, [messageText, conversation_id, user_id]);

    useEffect(() => {
        if (apiUrl && apiUrlRef.current !== apiUrl) {
            apiUrlRef.current = apiUrl;
            console.log('Fetching data...');
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
        if (setSelectedConversation && conversationReference && conversationRef.current !== conversationReference.id) {
            // trigger refresh of conversation history list
            console.log(`setting refresh flag with conversation reference conversationReference: ${JSON.stringify(conversationReference)} and conversationRef.current: ${conversationRef.current}`)
            setRefreshFlag && setRefreshFlag(true);
            conversationRef.current = conversationReference.id;
            const conversation: ConversationNew = { id: conversationReference.id, topic: conversationReference.topic, start_time: conversationReference.start_time };
            setSelectedConversation(conversation);
        }
        //change
    }, [conversationReference])// Dependency array, the effect runs when the URL changes


    useEffect(() => {

        if (updateHistory && ragResponse && ragRef.current !== ragResponse.response) {
            console.log(`ragResponse: ${ragResponse.response}`)
            const ru: MessageSimple = { role: "system", message: ragResponse.response, created_at: { $date: Date.now() } };
            updateHistory && updateHistory(ru);
        }
        if (updateHistory && kickbackResponse && kickbackRef.current !== kickbackResponse.follow_up_question) {
            console.log(`kickbackResponse: ${kickbackResponse.follow_up_question}`)
            const followUpQuestion: MessageSimple = { role: "system", message: kickbackResponse.follow_up_question, created_at: { $date: Date.now() } };
            updateHistory && updateHistory(followUpQuestion);
        }


        if (setAppStatus && 
            kickbackResponse &&
            ragResponse &&
            (kickbackResponse?.follow_up_question !== kickbackRef.current || noKickback) && 
            ragResponse?.response !== ragRef.current) {
            console.log(`resetting app status to idle with all responses in place`)

            if (kickbackResponse) {
                kickbackRef.current = kickbackResponse.follow_up_question
                setKickbackResponse(null)
            }
            if (ragResponse) {
                ragRef.current = ragResponse.response
                setRagResponse(null)
            }
            setRefreshFlag && setRefreshFlag(true);
            setAppStatus(AppStatus.Idle);
        }
    }, [kickbackResponse, ragResponse])
    // I am making a change!

    return { isNewConversation: conversationReference?.id !== conversationRef.current};
};

export default useQnAData;
