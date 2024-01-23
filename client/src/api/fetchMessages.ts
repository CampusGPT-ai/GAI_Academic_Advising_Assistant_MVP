import axios from 'axios';
import Message, { Citation, Followup } from '../model/messages/messages';
import { BaseUrl } from "./baseURL";

interface fetchMessagesParams {
  institution: string;
  user: string;
  conversationId: string;
}

const fetchMessageHistory = async ({
  institution,
  user,
  conversationId,
}: fetchMessagesParams): Promise<Message[]> => {
  const apiUrl = `${BaseUrl()}/institutions/${institution}/users/${user}/conversations/${conversationId}/messages`;
  const messages: Message[] = [];
  console.log(`fetching messages for conversationId: ${JSON.stringify(conversationId)}`)
  try {
    const response = await axios.get(apiUrl, {});
    
    if (response.data && Array.isArray(response.data)) {
      console.log(`Got response from messages API: ${JSON.stringify(response.data)}`)

      response.data.forEach(item => {

        const citations: Citation[] = item.citations.map((citation: { citation_path: string; citation_text: string; }) => ({
          CitationPath: citation.citation_path,
          CitationText: citation.citation_text,
        }));
        
        const followUps: Followup[] = item.follow_up_questions.map((followup: string) => ({
          FollowupQuestion: followup,
        }));

        messages.push({
          role: 'user',
          message: item.user_question,
        });
        messages.push({
          role: 'bot',
          message: item.bot_response,
          Citations: citations,
          Followups: followUps,
        });

        });
        return messages
      
    } else {
      console.log('Unexpected response format:', response);
      throw new Error('Unexpected response format');
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export default fetchMessageHistory;
