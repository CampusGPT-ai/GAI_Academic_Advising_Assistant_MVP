import axios from 'axios';

import { BaseUrl } from "./baseURL";

import { MessageSimple } from '../model/messages/messages';
import fetchParams from './fetchQuestions';

export interface FetchReviewCountResult {
    total_users_with_one_review: number,
    total_users_with_five_reviews: number
}

const fetchReviewCount = async ():Promise<FetchReviewCountResult> => {
    const apiUrl = `${BaseUrl()}/review-count`;
    console.log(`fetching review count for user`)
    try {
      const response = await axios.get(apiUrl, {});
      const reviews = response.data;
      console.log(`Got response from review count API: ${JSON.stringify(reviews)}`)
      return reviews;
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        console.error('API error:', error.response?.status, error.response?.data);
        if (error.response?.status === 401) {
          throw new Error('Unauthorized'); // Specific handling for 401 error
        } else {
          // Optional: Handle other specific status codes if necessary
          console.error('Unhandled API error', error.response
          ?.status);
          throw new Error('Error fetching messages');
          }
    } else {
        // Non-Axios error
        console.error('Non-Axios error:', error);
        throw new Error('Error fetching messages');
      }
    };

};

export default fetchReviewCount;