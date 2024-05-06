import axios from 'axios';
import Conversation from "../model/conversation/conversations";
import { BaseUrl } from "./baseURL";

interface fetchConversationsParams {
  user?: string;
}

interface ConversationsApiResponse {
  message: string;
  data?: Conversation[];
  error?: string;
}

const fetchConversations = async ({
  user,
}: fetchConversationsParams): Promise<ConversationsApiResponse> => {
  const apiUrl = `${BaseUrl()}/users/${user}/conversations`;

  // console.log("pinging for conversations API: ",apiUrl)

  try {
    const response = await axios.get(apiUrl, {});

    if (response.status === 204)
    {
      console.log(`no history found for user ${user}`)
      return {message: 'no history found'}
    }
    
    if (response.data && Array.isArray(response.data)) {
      //console.log(`Got response from conversations API: ${JSON.stringify(response.data)}`)
      const result = response.data.map(convo => ({
        id: convo.id,
        topic: convo.topic,
        start_time: convo.start_time,
        end_time: convo.end_time ? convo.end_time : undefined,
      }))
      return {message: 'message', data: result}
    } else {
      console.error('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error: any) {
    if (axios.isAxiosError(error) && error.response) {
      console.error('API error:', error.response.status, error.response.data);
      if (error.response.status === 401) {
        throw new Error('Unauthorized'); // Specific handling for 401 error
      } else {
        // Generic error handling
        throw new Error('Failed to fetch conversations');
      }
    } else {
      // Handling non-Axios errors
      console.error('Unexpected Error in response');
      throw new Error('An unexplained error occurred');
    }
  }
};
export default fetchConversations;
