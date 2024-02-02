import { Timestamp } from "../messages/messages";

type Conversation = {
    id: string;
    topic?: string;
    start_time: Timestamp;
    end_time?: Timestamp;
};


export default Conversation;