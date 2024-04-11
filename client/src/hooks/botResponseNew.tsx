import { useState, useEffect } from 'react';
import { Citation } from '../model/messages/messages';
import { ConversationNew } from '../model/conversation/conversations';
import AppStatus from '../model/conversation/statusMessages';
import cancelConversations from '../api/cancelChatResponse';

interface StreamData {
  taskId?: string;
  message?: string;
  question?: string;
  risks: string[];
  opportunities: string[];
  isStreaming: boolean;
  streamingError?: string;
}



function useStreamDataNew(
  setAppStatus: (appStatus: AppStatus) => void, 
  apiUrl?: string, 
  setSelectedConversation?: (conversation: ConversationNew) => void,
  setIsError?: (isError: boolean) => void,
  setNotification?: (notification: string) => void,
  ): StreamData {
  const [message, setMessage] = useState<string>();
  const [question, setQuestion] = useState<string>();
  const [risks, setRisks] = useState<string[]>([]);
  const [opportunities, setOpportunities] = useState<string[]>([]);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [error, setError] = useState<string>();
  const [taskId, setTaskId] = useState<string>();

  useEffect(() => {
    console.log(`task id changed to ${taskId}`)
  },[taskId])

  useEffect(() => {
    if (apiUrl) {
      console.log(`starting stream with url ${apiUrl}`)
      let isMounted=true;
      !isStreaming && setIsStreaming(true);

      const source = new EventSource(apiUrl);

      if (isMounted) {

        source.addEventListener('task_id', event => {
          const data = JSON.parse(event.data);
          console.log(`got task id from event source ${JSON.stringify(data)}`)
          setTaskId(data.task_id);
        });

        source.addEventListener('conversation', event => {
          const data = JSON.parse(event.data);
          console.log(`got conversation response from event source ${data.message.id}`)
          //this should be a whole conversation object (might need new one for simple conversation)
          setSelectedConversation && setSelectedConversation(data.message);
        });

        source.addEventListener('rag_response', event => {
          const data = JSON.parse(event.data);
          // console.log(`got rag response from event source ${data.message.response}`)
 
          setMessage(prev => prev + data.message.response);
          
        });

        source.addEventListener('notification', event => {
          const data = JSON.parse(event.data);
          // console.log(`got notification from event source ${data.message}`)   
        });

        source.addEventListener('error_message', event => {
          const data = JSON.parse(event.data);
          // console.log(`got error from event source ${data.message}`)
          cancelConversations({task_id: taskId})
          setError(data.message);
          return;
        });

        source.addEventListener('kickback_response', event => {
          const data = JSON.parse(event.data);
          // console.log(`got follow up q response from event source ${JSON.stringify(data)}`)

          if (data.message.follow_up_question) {
          setQuestion(prev => prev + data.message.follow_up_question);
          }
          
        });

        source.addEventListener('risks', event => {

          const data = JSON.parse(event.data);
          setRisks(prevRisks => [...prevRisks, data.message]);
      
        });

        source.onerror = (event) => {
          console.log(`error detected in event source ${event}`)
          setIsError && setIsError(true);
          setAppStatus(AppStatus.Error)
          setNotification && setNotification('An error occurred. Please try again later.')
          cancelConversations({task_id: taskId})
          source.close();
        }

        source.addEventListener('opportunities', event => {
          const data = JSON.parse(event.data);
          // console.log(`got opportunities from event source ${event.data}`)
   
          if (data.message) {
          setOpportunities(prevOpportunities => [...prevOpportunities, ...data.message])};
         
        });
      }

        //cleanup - close source, change streaming indicator, reset streaming message
        // console.log(`detecting event listener for stream ended`)
        source.addEventListener('stream-ended', () => {
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


  useEffect(()=>{
    !isStreaming && setMessage('');
    !isStreaming && setQuestion('');
  },[isStreaming])

  return {taskId, message, question, risks, opportunities, isStreaming, streamingError: error
   };
}

 export default useStreamDataNew;