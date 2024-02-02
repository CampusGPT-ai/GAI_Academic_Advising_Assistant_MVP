// Mock API function
import messageSample from "../model/messages/messageSample.json";
import { BaseUrl } from "./baseURL";

const jsonString = JSON.stringify(messageSample);

interface FetchMessagesParams {
  conversation_id: string;
  messageText: string;
  user_id?: string;
}

const fetchMessage = (
  { conversation_id, messageText, user_id}: FetchMessagesParams,
  onStreamDone: () => void,
  onStreamOpen: () => void,
  onMessageRecieved: (event: Event) => void,
  onTopicRecieved: (event: Event) => void,
  onFollowupsRecieved: (event: Event) => void,
  onError: (event: Event) => void,
) => {
  try {
    //choose endpoint depending on whether user is logged in and whether conversation exists
    let apiUrl = ''
    if (user_id && user_id != null) {
      if (conversation_id && conversation_id != null && conversation_id != 'null') {
        apiUrl =  `${BaseUrl()}/users/${user_id}/conversations/${conversation_id}/chat/${messageText}`
      } else{
        apiUrl =  `${BaseUrl()}/users/${user_id}/chat/${messageText}`
      }
    } 

    console.log("got api url: ",apiUrl)
    const sse = new EventSource(apiUrl); //{ withCredentials: false });
    sse.addEventListener('message', onMessageRecieved)
    sse.addEventListener('topic',onTopicRecieved)
    sse.addEventListener('followups',onFollowupsRecieved)
    sse.addEventListener('error',onError)

    sse.onopen = function (event) {
      console.log("EventSource connection opened.");
      onStreamOpen()
    }

    sse.onerror = (event) => {
      console.log("EventSource error occurred.");
      console.log("EventSource readyState: ", sse.readyState);
      sse.close();
      onStreamDone();
      onError(event);
  };

    return () => {
      console.log("closing connection in return function")
      onStreamDone();
      sse.close();
    };
  } catch (error) {
    console.log(`Error connecting to event source data in setup: ${error}`)
    return;
  }
};

export default fetchMessage;
