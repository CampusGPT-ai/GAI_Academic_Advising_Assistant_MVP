import { useState, useEffect } from 'react';
import { Citation } from '../model/messages/messages';
import { ConversationNew } from '../model/conversation/conversations';
import AppStatus from '../model/conversation/statusMessages';


interface StreamData {
  message?: string;
  risks: string[];
  opportunities: string[];
  isStreaming: boolean;
  streamingError?: string;
}



function useStreamDataNew(
  setAppStatus: (appStatus: AppStatus) => void, 
  apiUrl?: string, 
  setSelectedConversation?: (conversation: ConversationNew) => void, 
  getSelectedConversationMessages?: () => void,
  setIsError?: (isError: boolean) => void,
  setNotification?: (notification: string) => void,
  ): StreamData {
  const [message, setMessage] = useState<string>();
  const [risks, setRisks] = useState<string[]>([]);
  const [opportunities, setOpportunities] = useState<string[]>([]);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [error, setError] = useState<string>();


  useEffect(() => {
    if (apiUrl) {
      let isMounted=true;
      setIsStreaming(true);

      const source = new EventSource(apiUrl);

      if (isMounted) {
        setAppStatus(AppStatus.GeneratingChatResponse)

        source.addEventListener('conversation', event => {
          const data = JSON.parse(event.data);
          console.log(`got conversation response from event source ${data.message.id}`)
          //this should be a whole conversation object (might need new one for simple conversation)
          setSelectedConversation && setSelectedConversation(data.message);
        });

        source.addEventListener('rag_response', event => {
          const data = JSON.parse(event.data);
          console.log(`got rag response from event source ${data.message.response}`)
 
          setMessage(prev => prev + data.message.response);
          
        });

        source.addEventListener('notification', event => {
          const data = JSON.parse(event.data);
          console.log(`got notification from event source ${data.message}`)   
        });

        source.addEventListener('error_message', event => {
          const data = JSON.parse(event.data);
          console.log(`got error from event source ${data.message}`)
          setError(data.message);
          return;
        });

        source.addEventListener('kickback_response', event => {
          const data = JSON.parse(event.data);
          console.log(`got follow up q response from event source ${JSON.stringify(data)}`)

          if (data.message.follow_up_question) {
          setMessage(prev => prev + data.message.follow_up_question);
          }
          
        });

        source.addEventListener('risks', event => {

          const data = JSON.parse(event.data);
          setRisks(prevRisks => [...prevRisks, data.message]);
      
        });

        source.addEventListener('opportunities', event => {
          const data = JSON.parse(event.data);
          console.log(`got opportunities from event source ${event.data}`)
   
          if (data.message) {
          setOpportunities(prevOpportunities => [...prevOpportunities, ...data.message])};
         
        });
      }

        //cleanup - close source, change streaming indicator, reset streaming message
        console.log(`detecting event listener for stream ended`)
        source.addEventListener('stream-ended', () => {
          getSelectedConversationMessages && getSelectedConversationMessages()
          console.log(`stream end detected`)
          source.close();
          setMessage('');
          setIsStreaming(false);
          
      });
    

      return () => {
        isMounted=false;
        setIsStreaming(false);
        setAppStatus(AppStatus.Idle)
        source.close();
      }
    }
  }, [apiUrl]);

  useEffect(() =>{
    console.log(`detected change to streaming message value ${message}`)
  },[message])

  useEffect(()=>{
    !isStreaming && setMessage('');
  },[isStreaming])

  return { message, risks, opportunities, isStreaming, streamingError: error
   };
}

 export default useStreamDataNew;