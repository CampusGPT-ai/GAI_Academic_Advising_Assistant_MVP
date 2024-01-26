import { Meta } from "@storybook/react";
import ChatActive from "../../components/chat/chatContainer";

export default {
  component: ChatActive,
  title: "Sections/chat/ChatActive",
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} as Meta;

export const ExistingChat = {
  args: {
    convoTitle: "Chat with John Doe"
  },
};

export const NewChat = {
    args: {
      
    },
  };
  
  
