import { Meta } from "@storybook/react";
import Logo from "../../../components/header/headerCenterLogo";


export default {
    component: Logo,
    title: "Elements/Header/Logo",
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
    } as Meta;


    export const small = {
        args: {

        },
      };

    export const medium = {
        args: {
            size: "medium",
        },
      };

      export const large = {    
        args: {
            size: "large",
        },
      };
      
      