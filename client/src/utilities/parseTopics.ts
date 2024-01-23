import { Topic } from "../model/topic/topics";

/**
 * Finds topics by interest.
 * @param interests - An array of interests to filter topics by.
 * @param topics - An array of topics to filter.
 * @returns An array of unique question strings from the filtered topics.
 */
function findTopicsByInterest(interests: string[], topics: Topic[]): string[] {
  const lowerCaseInterests = interests.map((interest) =>
    interest.toLowerCase()
  );

  const filteredTopics = topics.filter((topic) => {
    if (topic.related_interests && topic.related_interests.interestList) {
      for (const interest of topic.related_interests.interestList) {
        if (lowerCaseInterests.includes(interest.toLowerCase())) {
          return true;
        }
      }
    }

    return false;
  });

  //console.log("Filtered topics: ", JSON.stringify(filteredTopics));
  return Array.from(new Set(filteredTopics.map((topic) => topic.question)));
}

/**
 * Gets the first three questions from the list of topics.
 * @param topics - An array of topics to retrieve questions from.
 * @returns An array of the first three question strings from the topics.
 */
export function getFirstThreeQuestions(topics: Topic[]): string[] {
  const processedTopics = preprocessTopics();
  // Filter topics where related_interests include 'starter'
  const filteredTopics = processedTopics.filter((topic) => {
    //console.log(`topic: ${JSON.stringify(topic)}`)
    if (topic.related_interests && topic.related_interests.interestList && topic.related_interests.interestList.includes("starter") ) {
     return true;
      
    }

    return false;
  });

  
  console.log(`filtered topics: ${filteredTopics}`)
  // Shuffle the filtered topics to randomize them
  for (let i = filteredTopics.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [filteredTopics[i], filteredTopics[j]] = [filteredTopics[j], filteredTopics[i]];
  }

  // Map the randomized topics to their questions
  const questions = filteredTopics.map((topic) => topic.question);

  // Return the first three questions from the randomized list
  // If there are less than three, it returns whatever is available
  return questions.slice(0, 3);
}


import topicSample from "../model/topic/topicSample.json";

// Function to process the JSON data and convert related_interests into the desired format
/**
 * Preprocesses the topic data by splitting the related_interests string into an array of strings,
 * each representing an interest. If related_interests is empty or undefined, it will result in an empty array.
 * @returns An array of Topic objects with the related_interests property as an object containing an interestList array.
 */
export function preprocessTopics(): Topic[] {
  const rawTopics = topicSample as any[]; // Temporarily treat the data as any type

  return rawTopics.map((rawTopic) => {
    // Splitting the related_interests string into an array of strings, each representing an interest
    // If related_interests is empty or undefined, it will result in an empty array
    const interests = rawTopic.related_interests
      ? {
          interestList: rawTopic.related_interests
            .toLowerCase()
            .split(",")
            .map((item: string) => item.trim()),
        }
      : { interestList: [] };

    return {
      ...rawTopic,
      related_interests: interests,
    };
  });
}

export default findTopicsByInterest;
