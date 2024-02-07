import { useState, useEffect } from 'react';
import { Citation } from '../model/messages/messages';
import { Followup } from '../model/messages/messages';
import Conversation from '../model/conversation/conversations';

interface StreamData {
  streamingMessage?: string;
  streamingConversation?: Conversation;
  citations: Citation[];
  followups: Followup[];
  isStreaming: boolean;
  streamingError?: string;
}



function useStreamData(apiUrl?: string): StreamData {
  const [streamingMessage, setStreamingMessage] = useState<string>();
  const [citations, setCitations] = useState<Citation[]>([]);
  const [conversation, setConversation] = useState<Conversation>();
  const [followups, setFollowups] = useState<Followup[]>([]);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [error, setError] = useState<string>();


  useEffect(() => {
    if (apiUrl) {
      let isMounted=true;
      setIsStreaming(true);

      const source = new EventSource(apiUrl);

      if (isMounted) {
        source.addEventListener('conversation', event => {
          const data = JSON.parse(event.data);
          setConversation(data.message);
        });

        source.addEventListener('message', event => {

          const data = JSON.parse(event.data);
          setStreamingMessage(prev => prev + data.message);
          
        });

        source.addEventListener('citations', event => {

          const data = JSON.parse(event.data);
          setCitations(prevCitations => [...prevCitations, data.citations]);
      
        });

        source.addEventListener('followups', event => {

          const data = JSON.parse(event.data);
          setFollowups(prevFollowups => [...prevFollowups, ...data.followups]);
         
        });
      }

        //cleanup - close source, change streaming indicator, reset streaming message
        console.log(`detecting event listener for stream ended`)
        source.addEventListener('stream-ended', () => {
          console.log(`stream end detected`)
          source.close();
          setStreamingMessage('');
          setIsStreaming(false);
          
      });
    

      return () => {
        isMounted=false;
        setIsStreaming(false);
        source.close();
      }
    }
  }, [apiUrl]);

  useEffect(() =>{
    console.log(`detected change to streaming message value ${streamingMessage}`)
  },[streamingMessage])

  useEffect(()=>{
    !isStreaming && setStreamingMessage('');
  },[isStreaming])

  return { streamingMessage, citations, followups, isStreaming, streamingError: error, streamingConversation: conversation
   };
}

 export default useStreamData;