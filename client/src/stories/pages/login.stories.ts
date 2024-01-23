//src/stories/pages/index.stories.ts
import { Meta } from "@storybook/react";
import Login from "../../components/pages/login";

export default {
    component: Login,
    title: "Pages/Login",
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
    argTypes: {
        getProfile: { action: 'getProfile' },

      },
    } as Meta;

  export const Primary = { args: { primary: true } };