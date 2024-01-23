import { Grid } from '@mui/material';
import { FC } from 'react';
import conversationSample from "../../../model/conversation/conversationSample.json";
import Conversation from '../../../model/conversation/conversations';
import ChatHistoryHeader from '../../elements/chatHistory/chatHistoryHeader';
import ChatHistoryList from '../../elements/chatHistory/chatHistoryList';

interface ChatHistoryContainerProps {
    conversations: Array<Conversation>;
    isLoading: boolean;
    setConversation: (conversationId: Conversation) => void;
    newChat: () => void;
    }
/**
 * Renders the container for the chat history section.
 * @param conversations - The list of conversations to display.
 * @param isLoading - A boolean indicating whether the conversations are currently being loaded.
 * @param setConversation - A function to set the active conversation.
 * @param newChat - A boolean indicating whether a new chat is being created.
 * @returns A React component that displays the chat history container.
 */
const ChatHistoryContainer: FC<ChatHistoryContainerProps> = (
    {conversations, isLoading, setConversation, newChat}
) => {
    return (
        <Grid container spacing={2} direction={"column"}
        sx={{
            borderRadius: 2, 
            boxShadow: 3, 
            overflow: 'hidden',
            backgroundColor: 'white',
            maxWidth: '400px',
        }}>
            <ChatHistoryHeader newChat={newChat} />
            <ChatHistoryList conversations={conversations} 
            convoIsLoading={isLoading} 
            setConversation={setConversation}/>
        </Grid>
    );
}

const jsonString = JSON.stringify(conversationSample);
const conversations = JSON.parse(jsonString) as Conversation[];

ChatHistoryContainer.defaultProps = {
    conversations: conversations,
    isLoading: false,
    setConversation: (item: Conversation) => {
        console.log(item);
      },
    newChat: () => {console.log("new chat clicked")},  

}

export default ChatHistoryContainer;
