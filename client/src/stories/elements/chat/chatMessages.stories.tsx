import { Meta } from "@storybook/react";
import ChatMessages from "../../../components/elements/chat/chatMessages";

export default {
  component: ChatMessages,
  title: "Elements/Chat/ChatMessages",
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
  
  
