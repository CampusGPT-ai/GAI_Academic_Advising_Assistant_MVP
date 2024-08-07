
export type Timestamp = {
    $date: number;
  };
  
  export type Citation = {
    citation_text: string;
    citation_path: string;
  };

  export type MessageSimple = {
    role: string;
    message: string;
    created_at: Timestamp;
    id?: string;
    citations?: Citation[];
    followups?: string[];
  }

  export type MessageContent = {
    role: string;
    message: string;
    created_at: Timestamp;
    id?: string;
  }

  export type Message = {
    id: string,
    user_session_id: string,
    message: MessageContent[];
  }
  
  type ParentMessage = {
    message: Message;
    citations?: Citation[];
    follow_up_questions?: string[];
  };
  
export default ParentMessage;