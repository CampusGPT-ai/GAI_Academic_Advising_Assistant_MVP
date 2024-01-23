import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import React, { FC, useState } from "react";
import dylan from "../../assets/images/avatars/dylan.png";
import jamal from "../../assets/images/avatars/jamal.png";
import tiffany from "../../assets/images/avatars/tiffany.png";
import Logo from "../../components/elements/header/headerCenterLogo"; // Update the path to where the Logo component is located
import { Topic } from "../../model/topic/topics";
import { UserProfile } from "../../model/user/user";
import { preprocessTopics } from "../../utilities/parseTopics";
import ProfilePhoto from "../elements/header/profilePhoto";
import ProfileDrawer from "./profileMenu";

const avatars: Map<string, string> = new Map();

avatars.set("dylan", dylan);
avatars.set("jamal", jamal);
avatars.set("tiffany", tiffany);

/**
 * Props for the Header component.
 * @interface
 * @property {string} title - The title to be displayed in the header.
 * @property {UserProfile | undefined} user - The user profile object, if the user is logged in.
 * @property {boolean} loggedIn - A boolean indicating whether the user is logged in or not.
 * @property {() => void} chatButtonClicked - A function to be called when the chat button is clicked.
 * @property {() => void} profileButtonClicked - A function to be called when the profile button is clicked.
 * @property {(list: string[]) => void} setSampleQuestions - A function to set the list of sample questions.
 */
interface HeaderProps {
  title: string;
  user: UserProfile | undefined;
  loggedIn: boolean;
  handleLogout: () => void;
  profileButtonClicked: () => void;
  setSampleQuestions: (list: string[]) => void;
}

const Header: FC<HeaderProps> = ({
  title,
  user,
  loggedIn,
  profileButtonClicked,
  handleLogout,
  setSampleQuestions,
}) => {
  const profileToolTip = loggedIn ? "Profile" : "Login";

  //initialize available topic/question pairs on header load.
  //This is used to populate the sample questions
  const [topics, setTopics] = useState<Topic[]>(preprocessTopics());
  const [isProfileMenuOpen, setProfileMenuOpen] = useState(false);

  /**
   * Toggles the profile menu open or closed.
   * If the user is not logged in, it triggers the profile button click event.
   * @param open - A boolean indicating whether the profile menu should be open or closed.
   * @param event - The keyboard or mouse event that triggered the toggle.
   */
  const toggleDrawer =
    (open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
      if (!loggedIn) {
        profileButtonClicked();
        return;
      }
      if (
        event &&
        event.type === "keydown" &&
        (event as React.KeyboardEvent).key === "Tab"
      ) {
        return;
      }
      setProfileMenuOpen(open);
    };

  return (
    <AppBar
      position="sticky"
      sx={{
        height: 80,
        backgroundColor: (theme) => theme.palette.primary.main,
      }}
    >
      <Toolbar
        sx={{
          height: "100%",
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        {/* Title */}
        <Typography variant="h4" component="div">
          {title}
        </Typography>

        {/* Icons */}
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Tooltip title={profileToolTip} arrow>
            <IconButton
              color="inherit"
              onClick={toggleDrawer(!isProfileMenuOpen)}
            >
              {user && (
                <ProfilePhoto
                  isLoggedIn={loggedIn}
                  imgPath={avatars.get(user.avatar)}
                />
              )}
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
      {/* Center Logo */}
      <Box
        sx={{
          position: "absolute",
          left: "50%",
          bottom: "0%",
          transform: "translate(-50%, 50%)",
          zIndex: 5,
        }}
      >
        <Logo size="small" />
      </Box>

      {user && (
        <ProfileDrawer
          setSampleQuestions={setSampleQuestions}
          handleLogout={handleLogout}
          user={user}
          avatar={avatars.get(user.avatar)}
          topics={topics}
          drawerOpen={isProfileMenuOpen}
          toggleDrawer={toggleDrawer}
        />
      )}
    </AppBar>
  );
};

//sample data for default props
import userSample from "../../model/user/userSample.json";
const jsonString = JSON.stringify(userSample);
const users = JSON.parse(jsonString) as UserProfile[];

Header.defaultProps = {
  title: "FSU CS Academy",
  loggedIn: true,
  user: users[0],
  profileButtonClicked: () => {
    console.log("profile button clicked");
  },
  setSampleQuestions: (list: string[]) => {
    console.log(list);
  },
};

export default Header;
