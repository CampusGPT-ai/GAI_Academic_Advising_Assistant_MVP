import React, { FC,useState } from 'react';
import ProfileCard from '../components/profileMenu/profileUserCard';
import { Box, Button } from '@mui/material';

interface LoginProps {
    getProfile: (id: string) => void; 
};

/**
 * Login component that displays a profile card and a login button.
 * @param {Object} props - Component props.
 * @param {Function} props.getProfile - Function to get the user profile.
 * @returns {JSX.Element} - Rendered component.
 */
const Login: FC<LoginProps> = (
    {
        getProfile
    }
) => {
    const [selectedProfile, setSelectedProfile] = useState<string>("");
        
    /**
     * Handles the change of the selected profile.
     * @param {string} id - The ID of the selected profile.
     */
    const handleProfileChange = (id: string) =>
    {
        setSelectedProfile(id);
    }
    return (
        
        <div>
           <ProfileCard setProfile={handleProfileChange} />
           <Box width="100%" justifyContent={"center"} display={"flex"}>
           <Button variant="contained" color="primary" onClick={() => getProfile(selectedProfile)}>Login</Button>
              </Box>
        </div>
    );
}

Login.defaultProps = {
    getProfile: (id: string) => {console.log(id)}
};

export default Login;
