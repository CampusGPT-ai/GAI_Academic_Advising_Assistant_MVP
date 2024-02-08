import React, { FC } from 'react';
import Divider from '@mui/material/Divider';
import { useTheme, Box, Drawer, Button } from '@mui/material';
import Conversation from '../../model/conversation/conversations';
import conversationSample from '../../model/conversation/conversationSample.json';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import DrawerContent from './drawerContent';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

//for default props
const jsonString = JSON.stringify(conversationSample);
const sampleMessages = JSON.parse(jsonString) as Conversation[];

const drawerWidth = 240;

interface Props {
  conversationList?: Conversation[];
  conversationFlag: boolean;
  handleSelectConversation: (conversation: Conversation) => void;
  resetConversation: () => void;
  account: any;
}

const DrawerContainer: FC<Props> = ({
    conversationList,
    handleSelectConversation,
    resetConversation,
    account,
    conversationFlag
}) => {
    const theme = useTheme()
    const h3Theme = theme.typography.h3;
    const [mobileOpen, setMobileOpen] = React.useState(false);
    const [isClosing, setIsClosing] = React.useState(false);
    const drawerWidth = 240;
  
  
    const handleDrawerClose = () => {
      setIsClosing(true);
      setMobileOpen(false);
    };
  
    const handleDrawerTransitionEnd = () => {
      setIsClosing(false);
    };
  
    const handleDrawerToggle = () => {
      if (!isClosing) {
        setMobileOpen(!mobileOpen);
      }
    };

    return (
        <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >

    <Drawer
variant="temporary"
open={mobileOpen}
onTransitionEnd={handleDrawerTransitionEnd}
onClose={handleDrawerClose}
ModalProps={{
  keepMounted: true, // Better open performance on mobile.
}}
color="#000"
sx={{
  display: { xs: 'flex', sm: 'none' },
  flexDirection: 'column', // Stack children vertically
  height: '100%', // Take full height
  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, backgroundColor: theme.palette.primary.light, },
}}
>
<DrawerContent conversationFlag={conversationFlag} conversationList={conversationList} handleSelectConversation={handleSelectConversation} resetConversation={resetConversation} />
</Drawer>
<Drawer
variant="permanent"
sx={{
  display: { xs: 'none', sm: 'block' },
  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, backgroundColor: theme.palette.primary.light, },
}}
open
>
<DrawerContent conversationFlag={conversationFlag} conversationList={conversationList} handleSelectConversation={handleSelectConversation} resetConversation={resetConversation} /> 
<Button variant="text" startIcon={<HelpOutlineOutlinedIcon  sx={{justifyContent: "flex-start"}}/>} >
  Need Help?
</Button>
<Divider />
<Box width={"80%"} mb={0} flexGrow={1}>
  <Box display="flex" flexDirection={"row"} justifyContent={"space-between"} alignItems={"center"} p={1}>
    <AccountCircleIcon />
    <Box flexGrow={1} p={1} sx={{ wordBreak: "break-all" }}>
      {account && account.name}
    </Box>
    <SettingsOutlinedIcon />
  </Box>
</Box>
</Drawer>
</Box>
    )
};

export default DrawerContainer;