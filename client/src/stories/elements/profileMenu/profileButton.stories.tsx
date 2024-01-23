import { Meta } from "@storybook/react";
import ProfileButtonComponent from "../../../components/elements/profileMenu/profileButton";


export default {
    component: ProfileButtonComponent,
    title: "Elements/ProfileMenu/ProfileButtonComponent",
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
    argTypes: {
        onButtonClick: { action: 'onButtonClick' },

      },
    } as Meta;


    export const basic = {
        args: {

        },
      };

