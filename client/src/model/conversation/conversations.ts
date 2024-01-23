type Conversation = {
    _id: string;
    user_id?: string;
    topic?: string;
    start_time: number;
    end_time?: number;
};


export default Conversation;