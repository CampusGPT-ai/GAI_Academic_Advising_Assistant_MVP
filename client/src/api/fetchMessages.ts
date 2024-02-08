import axios from 'axios';

import { BaseUrl } from "./baseURL";

import { MessageSimple } from '../model/messages/messages';

interface fetchMessagesParams {
  user: string;
  conversationId: string;
}

type FetchMessageHistoryResult = {
  type: 'messages';
  data: MessageSimple[];
} | {
  type: 'info';
  message: string;
};



const fetchMessageHistory = async ({
  user,
  conversationId,
}: fetchMessagesParams):Promise<FetchMessageHistoryResult> => {
  const apiUrl = `${BaseUrl()}/users/${user}/conversations/${conversationId}/messages`;
  console.log(`fetching messages for conversationId: ${JSON.stringify(conversationId)}`)

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

  } catch (error) {
    console.error(error);
    throw error;
  }

};

export default fetchMessageHistory;
