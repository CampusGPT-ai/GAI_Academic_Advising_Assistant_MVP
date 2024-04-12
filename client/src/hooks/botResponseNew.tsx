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

  function processMessage(event: any) {
    let data = event.data;
    if (typeof data === 'string') {
      data = JSON.parse(data); 
    }
    console.log(`Received data from event.  Data is ${JSON.stringify(data)}`)
    return data;
  }


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
          const data = processMessage(event);
          setTaskId(data.task_id);
        });

        source.addEventListener('conversation', event => {
          try {
            const data = processMessage(event);
            if (!data.message) {
              console.error('no message in conversation response')
              return;
            }
            const message = data.message
            const conversation : ConversationNew = {id: message.id, start_time: message.start_time };
            setSelectedConversation && setSelectedConversation(conversation);
          } catch (error) {
            setError("error parsing conversation response");
            setIsError && setIsError(true);
            console.error(`error parsing conversation response ${error}`)
          }
        });

        source.addEventListener('rag_response', event => {
          const data = processMessage(event);
          setMessage(data.message.response);
          
        });

        source.addEventListener('notification', event => {
          const data = processMessage(event);
        });

        source.addEventListener('error_message', event => {
          const data = processMessage(event);
          console.error(`got error from event source ${data.message}`)
          cancelConversations({task_id: taskId})
          setError(data.message);
          return;
        });

        source.addEventListener('kickback_response', event => {
          const data = processMessage(event);
          if (data.message.follow_up_question) {
          setQuestion(data.message.follow_up_question);
          }
          
        });

        source.addEventListener('risks', event => {
          const data = processMessage(event);
          setRisks(prevRisks => [...prevRisks, data.message]);
      
        });

        source.onerror = (event: any) => {
          console.log(`error detected in event source ${event}`)
          setIsError && setIsError(true);
          setAppStatus(AppStatus.Error)
          setNotification && setNotification('An error occurred. Please try again later.')
          cancelConversations({task_id: taskId})
          source.close();
        }

        source.addEventListener('opportunities', event => {
          const data = processMessage(event);
          // console.log(`got opportunities from event source ${event.data}`)
   
          if (data.message) {
          setOpportunities(prevOpportunities => [...prevOpportunities, ...data.message])};
         
        });
      }

        //cleanup - close source, change streaming indicator, reset streaming message
        // console.log(`detecting event listener for stream ended`)
        source.addEventListener('stream-ended', () => {
          console.log(`stream end detected`)
          if (isMounted) {
            setIsStreaming(false);
          }
          source.close();
          
      });
    

      return () => {
        isMounted=false;
        setIsStreaming(false);
        if (source) {
          source.close();
        }
      }
    }
  }, [apiUrl]);


  return {taskId, message, question, risks, opportunities, isStreaming, streamingError: error
   };
}

 export default useStreamDataNew;