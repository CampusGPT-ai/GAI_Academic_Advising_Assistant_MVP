import axios from 'axios';
import Conversation from "../model/conversation/conversations";
import { BaseUrl } from "./baseURL";

interface fetchConversationsParams {
  user?: string;
}

interface ConversationsApiResponse {
  data: Conversation[];
}

const fetchConversations = async ({
  user,
}: fetchConversationsParams): Promise<Conversation[]> => {
  const apiUrl = `${BaseUrl()}/users/${user}/conversations`;

  console.log("pinging for conversations API: ",apiUrl)

  try {
    const response : ConversationsApiResponse = await axios.get(apiUrl, {});
    
    if (response.data && Array.isArray(response.data)) {
      //console.log(`Got response from conversations API: ${JSON.stringify(response.data)}`)
      return response.data.map(convo => ({
        id: convo.id,
        topic: convo.topic,
        start_time: convo.start_time,
        end_time: convo.end_time ? convo.end_time : undefined,
      }));
    } else {
      console.error('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export default fetchConversations;
