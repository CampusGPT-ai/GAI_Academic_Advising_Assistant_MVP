import axios from 'axios';
import Conversation from "../model/conversation/conversations";
import { BaseUrl } from "./baseURL";

interface Params {
  user: string;
}

interface ConversationApiResponse {
  data: Conversation;
}

const fetchConversationId = async ({
  user,
}: Params): Promise<Conversation> => {
  const apiUrl = `${BaseUrl()}/users/${user}/save_conversation`;

  console.log("pinging for conversations API: ",apiUrl)

  try {
    const response : ConversationApiResponse = await axios.get(apiUrl, {});
    
    if (response.data) {
      console.log(`Got response from conversations API: ${JSON.stringify(response.data)}`)
      return response.data
    } else {
      console.log('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export default fetchConversationId;
