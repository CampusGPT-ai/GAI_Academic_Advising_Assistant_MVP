import axios from 'axios';
import Conversation from "../model/conversation/conversations";
import { BaseUrl } from "./baseURL";

interface fetchConversationsParams {
  institution: string;
  user: string;
}

const fetchConversations = async ({
  institution,
  user,
}: fetchConversationsParams): Promise<Conversation[]> => {
  const apiUrl = `${BaseUrl()}/institutions/${institution}/users/${user}/conversations`;

  console.log("pinging for conversations API: ",apiUrl)

  try {
    const response = await axios.get(apiUrl, {});
    
    if (response.data && Array.isArray(response.data)) {
      console.log(`Got response from conversations API: ${JSON.stringify(response.data)}`)
      return response.data.map(convo => ({
        _id: convo._id.$oid,
        user_id: convo.user.$oid,
        topic: convo.topic,
        start_time: convo.start_time.$date,
        end_time: convo.end_time ? convo.end_time.$date : undefined,
      }));
    } else {
      console.log('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export default fetchConversations;
