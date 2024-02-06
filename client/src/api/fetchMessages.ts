import axios from 'axios';
import ParentMessage, { Citation, Followup, Message } from '../model/messages/messages';
import { BaseUrl } from "./baseURL";
import Conversation from '../model/conversation/conversations';

interface fetchMessagesParams {
  user: string;
  conversationId: string;
}


const fetchMessageHistory = async ({
  user,
  conversationId,
}: fetchMessagesParams): Promise<ParentMessage[]> => {
  const apiUrl = `${BaseUrl()}/users/${user}/conversations/${conversationId}/messages`;
  console.log(`fetching messages for conversationId: ${JSON.stringify(conversationId)}`)

  try {
      // Making the axios call and expecting the response to be of type ApiMessage
      const response = await axios.get(apiUrl, {});
      //console.log(`recieved data from api: ${JSON.stringify(response)}`)
      const chats: ParentMessage[] = []
      // console.log(`recieved response.data from api: ${JSON.stringify(response.data)}`)
      const parsedData = JSON.parse(response.data)
      // console.log(`recieved response.data[0] from api: ${JSON.stringify(parsedData[0])}`)
      // console.log(`recieved response.data[0].messages from api: ${JSON.stringify(parsedData[0].messages)}`)
      // Extracting data from response
      if (parsedData[0].messages.length>0) {
        parsedData[0].messages.forEach((message: ParentMessage) => {
        chats.push(message)
       }
       );
      }
      // console.log(`returning list of parent messages ${JSON.stringify(chats)}`)
      return chats;

  } catch (error) {
    console.error(error);
    throw error;
  }

};

export default fetchMessageHistory;
