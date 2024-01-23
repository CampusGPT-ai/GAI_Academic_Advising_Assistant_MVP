import { Grid } from "@mui/material";
import Drawer from "@mui/material/Drawer";
import React, { FC, useState } from "react";
import { Topic } from "../../model/topic/topics";
import { UserProfile } from "../../model/user/user";
import findTopicsByInterest, { preprocessTopics } from "../../utilities/parseTopics";
import ProfileButtonContainer from "../elements/profileMenu/profileButtonContainer";
import ProfileMenuHeader from "../elements/profileMenu/profileMenuHeader";
/**
 * Props for the ProfileDrawer component.
 * @param setSampleQuestions - A function that sets the list of sample questions.
 * @param user - The user profile object.
 * @param topics - An array of topics.
 * @param drawerOpen - A boolean value indicating whether the drawer is open or not.
 * @param toggleDrawer - A function that toggles the drawer.
 * @returns JSX element
 */
interface ProfileDrawerProps {
  setSampleQuestions: (list: string[]) => void;
  handleLogout: () => void;
  user: UserProfile;
  avatar?: string;
  topics: Topic[];
  drawerOpen: boolean;
  toggleDrawer: (toggleVal: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => void;
}

const ProfileDrawer: FC<ProfileDrawerProps> = ({
  setSampleQuestions,
  handleLogout,
  user,
  topics,
  avatar,
  drawerOpen,
  toggleDrawer,
}) => {

  //initialize topic list based on user interests (gathered from the profile)
  const [topicList, setTopicList] = useState<string[]>(
    findTopicsByInterest(user.interests, topics)
  );

  const doLogout = () => {
    console.log("logging out user");
    toggleDrawer(false);
    handleLogout();
  }

  const onInterestChange = (list: string[]) => {
    //console.log("resetting topics based on selected interests interests", list);
    setTopicList(findTopicsByInterest(list, topics));
  };

  return (
    <Drawer anchor="top" open={drawerOpen} onClose={toggleDrawer(false)}>
      <div role="presentation"      >
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <ProfileMenuHeader user={user} avatar={avatar} handleLogout={doLogout} />
          </Grid>
          <Grid item xs={12}>
            <ProfileButtonContainer
              inputList={user.interests}
              handleSelectedValues={onInterestChange}
              title={"Interests"}
            />
          </Grid>
          <Grid item xs={12}>
            <ProfileButtonContainer
              inputList={topicList}
              handleSelectedValues={setSampleQuestions}
              title={"Suggestions for you"}
            />
          </Grid>
        </Grid>
      </div>
    </Drawer>
  );
};

//sample data for default props
import userSample from "../../model/user/userSample.json";
const jsonString = JSON.stringify(userSample);
const users = JSON.parse(jsonString) as UserProfile[];

ProfileDrawer.defaultProps = {
  setSampleQuestions: (list: string[]) => {
    console.log(list);
  },
  user: users[0],
  topics: preprocessTopics(),
  drawerOpen: false, // Default state could be closed
  toggleDrawer: (toggleVal: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
    console.log('Drawer toggled'); 
  },
};

export default ProfileDrawer;
