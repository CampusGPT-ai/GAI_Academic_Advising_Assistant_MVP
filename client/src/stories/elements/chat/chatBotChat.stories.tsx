import { Meta } from "@storybook/react";
import ChatBotChat from "../../../components/chat/chatElements/chatMessageElements/chatBotChat";


export default { component: ChatBotChat, title: "Elements/Chat/ChatBotChat" } as Meta;

export const ShortText = {
  args: {
    message: "Hello, how can I help you today?"
  },
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    isLoading: {description: "controls whether to show loading screen", control: 'boolean'},
    isError: {description: "controls error handling",control: 'boolean'},
    error: {control: 'text'},
    message: {description: "expected json input to parse to message object from API"}
  },
  
};

export const LongText = {
  args: {
    message: "Hello, how can I help you today? This is some long text. This is some long text. This is some long text. This is some long text. This is some long text.  "
  }
};

export const Error = {
  args: {
    isError: true,
    error: "Error"
  }
};

export const Loading = {
  args: {
    isLoading: true
  }
};
