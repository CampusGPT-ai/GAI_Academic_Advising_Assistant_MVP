import React, { FC, useState } from 'react';
import Divider from '@mui/material/Divider';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import List from '@mui/material/List';
import { Typography, useTheme, Box } from '@mui/material';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import MailIcon from '@mui/icons-material/Mail';
import Toolbar from '@mui/material/Toolbar';
import Conversation from '../../model/conversation/conversations';
import conversationSample from '../../model/conversation/conversationSample.json';
import QuestionAnswerOutlinedIcon from "@mui/icons-material/QuestionAnswerOutlined";
import HistoryIcon from '@mui/icons-material/History';
//for default props
const jsonString = JSON.stringify(conversationSample);
const sampleMessages = JSON.parse(jsonString) as Conversation[];

const drawerWidth = 240;

interface Props {
  conversationList: Conversation[];
  handleSelectConversation: (conversation: Conversation) => void;
  resetConversation: () => void;
}

const DrawerContent: FC<Props> = ({
  conversationList,
  handleSelectConversation,
  resetConversation,

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
 
          <ListItemButton onClick={() => resetConversation()}>
            <ListItemIcon >
              <QuestionAnswerOutlinedIcon color="primary" fontSize="medium" />
            </ListItemIcon>
            <ListItemText disableTypography primary=
              {<Typography variant="h6" style={{ color: '#000' }}>New Chat</Typography>} />
          </ListItemButton>


        <ListItem>
          <ListItemIcon >
            <HistoryIcon color="primary" fontSize="medium" />
          </ListItemIcon>
          <ListItemText disableTypography primary=
            {<Typography variant="h6" style={{ color: '#000' }}>Chat History</Typography>} />
        </ListItem>
        {conversationList.map((conversation, index) => (
          <ListItem key={index} disablePadding>
            <ListItemButton onClick={() => handleSelectConversation(conversation)}>

              <ListItemText disableTypography primary=
                {<Typography variant="body1" marginLeft={4} style={{ color: '#000' }}>{conversation.topic}</Typography>} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
}

DrawerContent.defaultProps = {
  conversationList: sampleMessages,
};


export default DrawerContent;