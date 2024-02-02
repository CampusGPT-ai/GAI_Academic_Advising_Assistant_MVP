
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

  export type Message = {
    role: string;
    message: string;
    created_at: Timestamp;

  }
  
  type ParentMessage = {
    messages: Message[];
    citations?: Citation[];
    follow_up_questions?: Followup[];
    user_session_id?: string;
  };
  
export default ParentMessage;