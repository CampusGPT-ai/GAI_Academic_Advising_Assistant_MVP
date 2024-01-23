  // Mock API function

  import topicSample from "../model/topic/topicSample.json";
import { Topic } from "../model/topic/topics";
 
  const jsonString = JSON.stringify(topicSample);
 
   const fetchTopics = ({/*jsonString: string*/}): Topic[] => {
     try {
       const topic = JSON.parse(jsonString) as Topic[];
       //console.log("parsing topics from topic list: " + topic)
       return topic;
     } catch (error) {
       console.error('Failed to parse the JSON string:', error);
       return [];
     }
   };
   
   export default fetchTopics;
 