import axios from 'axios';

import { BaseUrl } from "./baseURL";

import { MessageSimple } from '../model/messages/messages';

interface fetchMessagesParams {
  user: string;
  conversationId: string;
}

interface FetchMessageHistoryResult {
  type: 'info' | 'messages';
  message?: string;
  data?: MessageSimple[];
  error?: string;
}


const fetchMessageHistory = async ({
  user,
  conversationId,
}: fetchMessagesParams):Promise<FetchMessageHistoryResult> => {
  const apiUrl = `${BaseUrl()}/users/${user}/conversations/${conversationId}/messages`;
  // console.log(`fetching messages for conversationId: ${JSON.stringify(conversationId)}`)

  try {
      // Making the axios call and expecting the response to be of type ApiMessage
      const response = await axios.get(apiUrl, {});

      if (response.status === 204) {
        return {type: 'info', message: 'no history found'}
      }
      // console.log(`recieved data from api: ${JSON.stringify(response)}`)
      const chats: MessageSimple[] = []
      // console.log(`recieved response.data from api: ${JSON.stringify(response.data)}`)
      const parsedData = JSON.parse(response.data)
      // console.log(`recieved response.data[0] from api: ${JSON.stringify(parsedData)}`)

      if (parsedData.length>0) {
        parsedData.forEach((message: MessageSimple) => {
        chats.push(message)
       }
       );
      }
      //console.log(`returning list of parent messages ${JSON.stringify(chats)}`)
      return { type: 'messages', data: chats };

  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      console.error('API error:', error.response?.status, error.response?.data);
      if (error.response?.status === 401) {
        return { type: 'info', message: 'Unauthorized access', error: 'Unauthorized' }; // Specific handling for 401 error
      } else {
        // Optional: Handle other specific status codes if necessary
        console.error('Unhandled API error', error.response?.status);
        return { type: 'info', message: 'Error fetching messages', error: 'API Error' };
      }
    } else {
      // Non-Axios error
      console.error('Error:', error.message);
      return { type: 'info', message: 'Failed to fetch messages', error: error.message };
    }
  }
};

export default fetchMessageHistory;
