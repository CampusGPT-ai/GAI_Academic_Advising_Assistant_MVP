import { Box, Button, Typography, useTheme } from "@mui/material";
import React, { FC } from "react";
import { UserProfile } from "../../model/user/user";
import ProfilePhoto from "../header/profilePhoto";


//for default props
import userSample from "../../model/user/userSample.json";
const jsonString = JSON.stringify(userSample);
const users = JSON.parse(jsonString) as UserProfile[];


interface ProfileMenuHeaderProps {
  user: UserProfile;
  avatar?: string;
  handleLogout: () => void;
}

const ProfileMenuHeader: FC<ProfileMenuHeaderProps> = ({ user, avatar, handleLogout }) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        backgroundColor: theme.palette.primary.main,
        width: "100%",
        display: "flex",
        alignItems: "center",
        padding: 1,
        justifyContent: 'space-between',
      }}
    >
      <ProfilePhoto isLoggedIn={true} imgPath={avatar} />
      &nbsp; &nbsp;
      <Typography variant="h6" color={theme.palette.primary.contrastText}> {user.full_name}</Typography>
      <Button variant="contained" onClick={handleLogout} sx={{backgroundColor: theme.palette.secondary.main, mr: 3}} >Logout</Button>
    </Box>
  );
};

ProfileMenuHeader.defaultProps = {};

ProfileMenuHeader.defaultProps = {
  user: users[0],
};

export default ProfileMenuHeader;
