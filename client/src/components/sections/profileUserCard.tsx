import { Box, Grid, Typography, useMediaQuery, useTheme } from "@mui/material";
import { FC, useEffect, useState } from "react";
import dylan from "../../assets/images/avatars/dylan.png";
import jamal from "../../assets/images/avatars/jamal.png";
import tiffany from "../../assets/images/avatars/tiffany.png";
import "../../assets/styles.css";
import { UserProfile } from "../../model/user/user";
import ProfilePhoto from "../elements/header/profilePhoto";

interface ProfileCardProps {
  users?: UserProfile[];
  setProfile: (id: string) => void;
}

/**
 * ProfileCard component displays a list of user profiles with their interests and academics.
 * @param {Object} props - Component props.
 * @param {Array} props.users - Array of user objects.
 * @param {Function} props.setProfile - Function to set the selected profile.
 * @returns {JSX.Element} - Rendered component.
 */
const ProfileCard: FC<ProfileCardProps> = ({ users, setProfile }) => {
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null);

  const theme = useTheme();
  const avatars: Map<string, string> = new Map();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("sm"));
  const isMedScreen = useMediaQuery(theme.breakpoints.down("md"));

  avatars.set("dylan", dylan);
  avatars.set("jamal", jamal);
  avatars.set("tiffany", tiffany);

  useEffect(() => {
    if (selectedProfile) {
      setProfile(selectedProfile);
    }
  }, [selectedProfile]);

  return (
    <Grid
      container
      direction="row"
      width="100%"
      sx={{ m: 3, justifyContent: "space-evenly" }}
    >
      {users &&
        users.map((user, index) => (
          <Grid
            direction="column"
            container
            key={index}
            className="demoProfileContainer"
            sx={{
              backgroundColor: theme.palette.primary.main,
              ":hover": {
                backgroundColor: theme.palette.secondary.main, // hover effect
              },
              border: selectedProfile === user.user_id ? "4px solid gray" : "none", // selected effect
            }}
            onClick={() => {
              console.log(user.user_id);
              setSelectedProfile(user.user_id);
            }}
          >
            <Box width="100%" justifyContent={"center"} display={"flex"} flexDirection={"column"} alignItems={"center"}>
              <Typography variant="h4">{user.full_name}</Typography>
              <br></br>
              <ProfilePhoto
                width={isSmallScreen ? "80px" : isMedScreen ? "120px" : "200px"}
                height={
                  isSmallScreen ? "80px" : isMedScreen ? "120px" : "200px"
                }
                isLoggedIn={true}
                imgPath={avatars.get(user.avatar)}
              />
            </Box>
            <Typography variant="h6" color={theme.palette.primary.contrastText}>
              Interests:{" "}
              <Box sx={{ ...theme.typography.body1 }}>
                {user.interests.join(", ")}
              </Box>{" "}
            </Typography>
     
            <Typography variant="h6" color={theme.palette.primary.contrastText}>
              Academics:{" "}
              <Box sx={{ ...theme.typography.body1 }}>
                {user.academics.AcademicYear &&
                  "Year: " + user.academics.AcademicYear}
                {user.academics.Major && user.academics.AcademicYear && ", "}
                {user.academics.Major && "Major: "}
                {user.academics.Major}
                {user.academics.Minor && ", Minor: " + user.academics.Minor}
              </Box>{" "}
            </Typography>

            <Typography variant="h6" color={theme.palette.primary.contrastText}>
              Course History:{" "}
              <Box sx={{ ...theme.typography.body1 }}>
              {user.courses?.join(", ")}
              </Box>{" "}
            </Typography>
          </Grid>
        ))}
      ;
    </Grid>
  );
};
//for default props
import userSample from "../../model/user/userSample.json";
const jsonString = JSON.stringify(userSample);
const usersimport = JSON.parse(jsonString) as UserProfile[];

ProfileCard.defaultProps = {
  users: usersimport,
  setProfile: (id: string) => {
    console.log(id);
  },
};

export default ProfileCard;
