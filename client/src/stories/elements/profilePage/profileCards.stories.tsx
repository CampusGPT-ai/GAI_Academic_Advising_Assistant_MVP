import { Meta } from "@storybook/react";
import ProfileCard from "../../../components/sections/profileUserCard";


export default {
    component: ProfileCard,
    title: "Elements/ProfilePage/ProfileCards",
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
    argTypes: {
      setSelectedProfile: { action: 'setSelectedProfile' },

      },
    } as Meta;


    export const basic = {
        args: {

        },
      };

