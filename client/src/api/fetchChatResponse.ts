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
  onStreamUpdate: (newResponse: string, isFirstChunk: boolean) => void,
  onMetaDataReceived: (newMetaData: any, message: string) => void,
  onStreamDone: () => void,
  onStreamOpen: () => void,
  onError: (error: Error) => void,
) => {
  try {
    //choose endpoint depending on whether user is logged in and whether conversation exists
    let apiUrl = ''
    if (user_id && user_id != null) {
      if (conversation_id && conversation_id != null && conversation_id != 'null') {
        apiUrl =  `${BaseUrl()}/institutions/demo/users/${user_id}/conversations/${conversation_id}/chat/${messageText}`
      } else{
        apiUrl =  `${BaseUrl()}/institutions/demo/users/${user_id}/chat/${messageText}`
      }
    } else
    {
      apiUrl = `${BaseUrl()}/chat/${messageText}`
    }
    console.log("got api url: ",apiUrl)
    const sse = new EventSource(apiUrl); //{ withCredentials: false });
    let messageBuffer = ''
    console.log("EventSource readyState: ", sse.readyState);

    sse.onopen = function (event) {
      console.log("EventSource connection opened.");
      onStreamOpen()
    }
    sse.onmessage = function (event) {
      let chunk = event.data
      console.log("received message chunk: ", chunk)
      if (chunk.startsWith("<<<META-DATA>>>")) {
        console.log("received meta-data chunk: " + chunk) 
        chunk = chunk.replace("<<<META-DATA>>>", "")
        // TODO: replace with real followups returned in response
        const data = JSON.parse(chunk);
        onMetaDataReceived(data, messageBuffer)
      }
      else {
        let isFirstChunk = messageBuffer.length == 0
        messageBuffer = messageBuffer + chunk
        onStreamUpdate(messageBuffer, isFirstChunk)
      }
  
    };

    sse.onerror = (event) => {
      console.log("EventSource error occurred.");
      console.log("EventSource readyState: ", sse.readyState);
      sse.close();
      onStreamDone();
      onError(new Error("Error event from EventSource: " + JSON.stringify(event)));
  };

    return () => {
      console.log("closing connection in return function")
      onStreamDone();
      sse.close();
    };
  } catch (error) {
    console.log(`Error event from EventSource: ${error}`)
    onError(new Error(`Error event from EventSource: ${error}`));
    return;
  }
};

export default fetchMessage;
