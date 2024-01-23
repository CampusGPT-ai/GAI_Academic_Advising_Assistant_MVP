import { Meta } from "@storybook/react";
import ChatUserChat from "../../../components/elements/chat/chatUserChat";

export default {
  component: ChatUserChat,
  title: "Elements/Chat/ChatUserChat",
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} as Meta;

export const ShortText = {
  args: {
    text: "Hello, how can I help you today?",
  },
};

export const LongText = {
  args: {
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, sapien vel bibendum lacinia, velit velit bibendum sapien, vel bibendum sapien velit bibendum sapien.",
  },
};
