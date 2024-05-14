import { Timestamp } from "../messages/messages";
import ParentMessage from "../messages/messages";
import { createContext } from "react";

type Conversation = {
    id: string;
    topic?: string;
    start_time: Timestamp;
    end_time?: Timestamp;
    messages?: ParentMessage[];
    user_id?: string,
};

export type ConversationNew = {
    id: string;
    topic?: string;
    start_time: Timestamp;
    end_time?: Timestamp;
    history?: any;
    user_id?: string,
};

export interface ConversationContextType {
    conversation: Conversation | null;
    userSession: string | null;
  }
  
  export const defaultConversation: Conversation = {
    id: "0",
    start_time: { $date: Date.now() },
  };
  
  export const defaultConversationContext: ConversationContextType = {
    conversation: null,
    userSession: null,
  };
  
  // Create the context
  export const ConversationContext = createContext<ConversationContextType>(defaultConversationContext);
  
  export default Conversation;