import axios from 'axios';
import Conversation from "../model/conversation/conversations";
import { BaseUrl } from "./baseURL";


interface responseParams {
  conversation_id: string;
    session_id: string;
    feedback: any;
    message_id: string; 
  }

  //@app.post("/users/{session_guid}/conversations/{conversation_id}/messages/{message_id}")
const submitChatFeedback = async ({conversation_id, session_id, feedback, message_id} : responseParams) => {
    try {
      const response = await axios.post(`${BaseUrl()}/users/${session_id}/conversations/${conversation_id}/messages/${message_id}`, feedback);
      console.log('Response from feedback API:', response.data);
      debugger; 
      // Additional logic based on response, if needed
    } catch (error) {
      console.error('Error submitting form:', error);
      // Handle error (e.g., display error message)
    }
  };

  export default submitChatFeedback;
