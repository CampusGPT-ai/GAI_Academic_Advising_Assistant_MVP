
export type Timestamp = {
    $date: number;
  };
  
  export type Citation = {
    citation_text: string;
    citation_path: string;
  };
  
  export type Followup = {
    question: string;
  };

  export type MessageSimple = {
    role: string;
    message: string;
    created_at: Timestamp;
    citations?: Citation[];
    follow_up_questions?: Followup[];
  }

  export type MessageContent = {
    role: string;
    message: string;
    created_at: Timestamp;
  }

  export type Message = {
    id: string,
    user_session_id: string,
    message: MessageContent[];
  }
  
  type ParentMessage = {
    message: Message;
    citations?: Citation[];
    follow_up_questions?: Followup[];
  };
  
export default ParentMessage;