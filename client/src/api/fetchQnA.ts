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
    setNewConversationFlag?: (isNewConversation: boolean) => void
    ) => {
    const [conversationReference, setConversationReference] = useState<ConversationReference | null>(null);
    const [kickbackResponse, setKickbackResponse] = useState<KickbackResponse | null>(null);
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
            setKickbackResponse(data.kickback_response);
            setRagResponse(data.rag_response);
            setConversationReference(data.conversation_reference);

            console.log('Data fetched:', JSON.stringify(data));
        } catch (error) {
            throw error;
        }

    };

    useEffect(() => {
        if (messageText) {
            if (userQuestionRef.current === messageText) {
                return;
            }
            else {
                
                if (user_id) {
                    if (conversation_id) {
                        setApiUrl(`${BaseUrl()}/users/${user_id}/conversations/${conversation_id}/chat_new/${messageText}`)
                    } else {
                        setNewConversationFlag && setNewConversationFlag(true);
                        setApiUrl(`${BaseUrl()}/users/${user_id}/conversations/0/chat_new/${messageText}`)
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
            conversationRef.current = conversationReference.id;
            const conversation: ConversationNew = { id: conversationReference.id, topic: conversationReference.topic, start_time: conversationReference.start_time };
            setSelectedConversation(conversation);
        }
    }, [conversationReference])// Dependency array, the effect runs when the URL changes

    useEffect(() => {
        if (updateHistory && ragResponse && ragRef.current !== ragResponse.response) {
            console.log(`ragResponse: ${ragResponse.response}`)
            ragRef.current = ragResponse.response;
            const ru: MessageSimple = { role: "system", message: ragResponse.response, created_at: { $date: Date.now() } };
            updateHistory && updateHistory(ru);
            setRagResponse(null);
        }
    }, [ragResponse])// Dependency array, the effect runs when the URL changes

    useEffect(() => {
        if (updateHistory && kickbackResponse && kickbackRef.current !== kickbackResponse.response) {
            console.log(`kickbackResponse: ${kickbackResponse.response}`)
            kickbackRef.current = kickbackResponse.response;
            const followUpQuestion: MessageSimple = { role: "system", message: kickbackResponse.follow_up_question, created_at: { $date: Date.now() } };
            updateHistory && updateHistory(followUpQuestion);
            setKickbackResponse(null);
        }
    }, [kickbackResponse])

    useEffect(() => {
        if (setAppStatus && kickbackResponse?.response === kickbackRef.current && ragResponse?.response === ragRef.current && conversationReference?.id === conversationRef.current) {
            setAppStatus(AppStatus.Idle);
        }
    }, [kickbackResponse, ragResponse, conversationReference])

    return { isNewConversation: conversationReference?.id !== conversationRef.current};
};

export default useQnAData;
