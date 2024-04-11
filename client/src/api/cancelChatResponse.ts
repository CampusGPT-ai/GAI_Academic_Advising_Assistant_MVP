import axios from 'axios';
import { BaseUrl } from "./baseURL";

interface CancelConversationsParams {
  task_id?: string;
}

const cancelConversations = async ({ task_id }: CancelConversationsParams) => {
  const apiUrl = `${BaseUrl()}/cancel-operation/${task_id}`;

  try {
    const response = await axios.post(apiUrl, {});

    if (response.status === 200) {
      console.log('Task ID cancelled successfully:', task_id);
    } else {
      console.error('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error) {
    console.error('Error cancelling task:', error);
    throw error;
  }
};

export default cancelConversations;
