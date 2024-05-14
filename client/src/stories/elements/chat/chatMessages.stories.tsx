import { Meta } from "@storybook/react";
import ChatMessages from "../../../components/chat/chatElements/chatMessageContainer";
import FeedbackForm from "../../../components/chat/chatElements/chatMessageElements/chatResponse/chatResponseFeedbackForm";

export default {
  component: FeedbackForm,
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

