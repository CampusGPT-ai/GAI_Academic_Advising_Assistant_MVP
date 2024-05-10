import axios from 'axios';
import Conversation from "../model/conversation/conversations";
import { BaseUrl } from "./baseURL";


interface responseParams {
    feedback: any;
  
  }

const submitChatFeedback = async ({feedback} : responseParams) => {
    try {
      const response = await axios.post('https://your-endpoint.com/api/feedback', feedback);
      console.log('Response:', response.data);
      // Additional logic based on response, if needed
    } catch (error) {
      console.error('Error submitting form:', error);
      // Handle error (e.g., display error message)
    }
  };

  export default submitChatFeedback;
