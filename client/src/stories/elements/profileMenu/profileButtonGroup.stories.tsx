import { Meta } from "@storybook/react";
import ButtonGroupComponent from "../../../components/elements/profileMenu/profileButtonGroup";


export default {
    component: ButtonGroupComponent,
    title: "Elements/ProfileMenu/ButtonGroupComponent",
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
    argTypes: {handleSelectedValues: {action: "handleSelectedValues"}},
    } as Meta;


    export const basic = {
        args: {

        },
      };