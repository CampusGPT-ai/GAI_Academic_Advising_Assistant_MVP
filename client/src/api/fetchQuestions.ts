import axios from 'axios';
import { BaseUrl } from "./baseURL";

interface fetchParams {
  user?: string;

}
interface FetchQuestionResult {
  messages?: string[];
  error?: string;
}


const fetchSampleQuestions = async ({
  user,
}: fetchParams):Promise<FetchQuestionResult> => {
  const apiUrl = `${BaseUrl()}/users/${user}/questions`;
  console.log(`fetching questions for user`)
  try {
    const response = await axios.get(apiUrl, {});
    //console.log("got data from questions api: ", JSON.stringify(response.data))
    
    const questions = response.data.data.questions;
    
    if (questions && Array.isArray(questions)) {
      //console.log(`Got response from questions API: ${JSON.stringify(questions)}`)

      questions.forEach((question : string) => {
        //console.log(question)
        });

      return {messages: questions.slice(0,4)};

      
    } else {
      console.error('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      console.error('API error:', error.response?.status, error.response?.data);
      if (error.response?.status === 401) {
        throw new Error('Unauthorized'); // Specific handling for 401 error
      } else {
        // Optional: Handle other specific status codes if necessary
        console.error('Unhandled API error', error.response?.status);
        throw new Error('Error fetching messages');
      }
    } else {
      // Non-Axios error
      console.error('Error:', error.message);
      throw new Error('An unexplained error occurred');
    }
  }
};

export default fetchSampleQuestions;
