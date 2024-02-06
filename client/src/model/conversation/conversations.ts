import { Timestamp } from "../messages/messages";
import ParentMessage from "../messages/messages";

type Conversation = {
    id: string;
    topic?: string;
    start_time: Timestamp;
    end_time?: Timestamp;
    messages?: ParentMessage[];
    user_id?: string,
};


export default Conversation;