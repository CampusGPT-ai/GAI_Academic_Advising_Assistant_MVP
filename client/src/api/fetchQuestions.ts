import axios from 'axios';
import { BaseUrl } from "./baseURL";

interface fetchParams {
  user?: string;

}


const fetchSampleQuestions = async ({
  user,

}: fetchParams): Promise<string[]> => {
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

      return questions.slice(0,4);

      
    } else {
      console.error('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export default fetchSampleQuestions;
