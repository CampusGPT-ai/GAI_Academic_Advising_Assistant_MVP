// Define the interest type which is a simple string 
export type Interest = string;

// Define the InterestsType, which is a container for an array of Interest
export type InterestsType = {
    interestList: Interest[] | null;
}

// Define the TopicType, which represents the entire data structure
export type Topic = {
    topic: string;
    question: string;
    answer: string;
    related_interests: InterestsType | null;
}
