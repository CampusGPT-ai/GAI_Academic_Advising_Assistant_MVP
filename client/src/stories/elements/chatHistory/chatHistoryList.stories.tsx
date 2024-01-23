import { Meta } from "@storybook/react";
import ChatHistory from "../../../components/elements/chatHistory/chatHistoryList";

export default {
  component: ChatHistory,
  title: "Elements/ChatHistory/ChatHistoryList",
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} as Meta;

export const loaded = {
  args: {
   
  },
};

export const loading = {
    args: {
     convoIsLoading: true,
     conversations: [],
    },
  };
  

  export const Empty = {
    args: {
     convoIsLoading: false,
     conversations: [],
    },
  };
  
