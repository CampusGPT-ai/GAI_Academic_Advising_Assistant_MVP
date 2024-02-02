import axios from 'axios';
import ParentMessage, { Citation, Followup, Message } from '../model/messages/messages';
import { BaseUrl } from "./baseURL";

interface fetchMessagesParams {
  user: string;
  conversationId: string;
}

interface NestedApiMessage {
  user_session_id: string;
  message: Message[];
  id: string;
}

interface ApiMessage {
  message?: NestedApiMessage;
  citations?: Citation[];
  follow_up_questions?: Followup[];
}

interface ApiResponse {
  end_time: string | null;
  topic: string;
  user_id: string;
  start_time: string;
  messages: ApiMessage[];
  id: string;
}


const fetchMessageHistory = async ({
  user,
  conversationId,
}: fetchMessagesParams): Promise<ParentMessage[]> => {
  const apiUrl = `${BaseUrl()}/users/${user}/conversations/${conversationId}/messages`;
  const chats: ParentMessage[] = [];
  console.log(`fetching messages for conversationId: ${JSON.stringify(conversationId)}`)
  try {
    const response = await axios.get<ApiResponse>(apiUrl, {});
    
    if (response.data && Array.isArray(response.data)) {
      console.log(`Got response from messages API: ${JSON.stringify(response.data)}`)

      response.data.forEach((chatSession : ApiResponse) => {
        
        chatSession.messages.forEach((item : ApiMessage) => {

          const chatMessages: Message[] = item.message?.message || [];

          const chat_message: ParentMessage = {
            messages: chatMessages,
            citations: item.citations,
            follow_up_questions: item.follow_up_questions,
            user_session_id: chatSession.id
          }

          chats.push(chat_message);
        });
      });
      return chats;

      
    } else {
      console.log('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export default fetchMessageHistory;
