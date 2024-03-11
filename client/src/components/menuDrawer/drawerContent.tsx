import React, { FC, useState } from 'react';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import { Typography, useTheme, Box , CircularProgress} from '@mui/material';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import Toolbar from '@mui/material/Toolbar';
import Conversation from '../../model/conversation/conversations';
import conversationSample from '../../model/conversation/conversationSample.json';
import QuestionAnswerOutlinedIcon from "@mui/icons-material/QuestionAnswerOutlined";
import HistoryIcon from '@mui/icons-material/History';
//for default props
const jsonString = JSON.stringify(conversationSample);
const sampleMessages = JSON.parse(jsonString) as Conversation[];

const drawerWidth = 240;

const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';

interface Props {
  conversationList?: Conversation[];
  conversationFlag: boolean;
  handleSelectConversation: (conversation: Conversation) => void;
  resetConversation: () => void;
}

const DrawerContent: FC<Props> = ({
  conversationList,
  handleSelectConversation,
  resetConversation,
  conversationFlag,
}) => {


  const theme = useTheme();
  /**
* Handles the selection of a conversation and updates the state accordingly.
* @param conversation - The conversation object that was selected.
*/


  return (
    <Box flexGrow="1" sx={{overflowY: "auto"}}>
      <Toolbar />
      <Divider />
      <List>
 
          <ListItemButton component="li" role="listitem" onClick={() => resetConversation()}>
            <ListItemIcon >
              <QuestionAnswerOutlinedIcon color="primary" fontSize="medium" />
            </ListItemIcon>
            <ListItemText disableTypography primary=
              {<Typography variant="h6" style={{ color: '#000' }}>New Chat</Typography>} />
          </ListItemButton>


        {AUTH_TYPE!=='NONE' && <ListItem>
          <ListItemIcon >
            <HistoryIcon color="primary" fontSize="medium" />
          </ListItemIcon>
          <ListItemText disableTypography primary=
            {<Typography variant="h6" style={{ color: '#000' }}>Chat History</Typography>} />
        </ListItem>}

        { AUTH_TYPE!=='NONE' && conversationList && conversationList.map((conversation, index) => (
          <ListItem key={index} disablePadding>
            <ListItemButton role="listitem" onClick={() => handleSelectConversation(conversation)}>

              <ListItemText disableTypography primary=
                {<Typography variant="body1" marginLeft={4} style={{ color: '#000' }}>{conversation.topic}</Typography>} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      {AUTH_TYPE!=='NONE' && !conversationList && conversationFlag && <Box m={2}><CircularProgress
            size={20}
            thickness={5}
            style={{ marginLeft: 10 }}
            aria-label="loading conversation"
          /> </Box>}
      {AUTH_TYPE!=='NONE' && !conversationFlag && <Box m={2}>You haven't started any conversations yet.  Ask a question to begin!</Box>}
        

    </Box>
  );
}

export default DrawerContent;
