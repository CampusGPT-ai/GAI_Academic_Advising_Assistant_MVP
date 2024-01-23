
export type Timestamp = {
    $date: number;
  };
  
  export type Citation = {
    CitationPath: string;
    CitationText: string;
  };
  
  export type Followup = {
    FollowupQuestion: string;
  };
  
  type Message = {
    //_id?: string; //could drop
    //user?: string; //don't use it
    //conversation?: string; //don't use this in the message
    //timestamp?: Timestamp; //don't do anything with it
    role: string;
    message: string;
    topic?: string;
    Citations?: Citation[];
    Followups?: Followup[];
  };
  
export default Message;