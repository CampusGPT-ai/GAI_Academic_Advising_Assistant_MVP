import { Meta } from "@storybook/react";
import ProfileDrawer from "../../components/profileMenu/profileMenu";


export default {
    component: ProfileDrawer,
    title: "sections/ProfileDrawer",
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"], 
    argTypes: {
        toggleDrawer: { action: 'toggleDrawer' },
        setSampleQuestions: {action: 'setSampleQuestions'},

      },

    } as Meta;


    export const basic = {

      };

