import { Meta } from "@storybook/react";
import { userEvent, waitFor, within } from '@storybook/testing-library';
import ChatInput from "../../../components/chat/chatElements/chatInput";
import AppStatus from "../../../model/conversation/statusMessages";

export default {
  component: ChatInput,
  title: "Elements/Chat/ChatInput",
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  args: {appStatus: AppStatus.Idle},
} as Meta;

export const Basic = {
  args: {
   
  },
};