import { Meta } from "@storybook/react";
import ChatBotChat from "../../../components/chat/chatElements/chatMessageElements/chatBotChat";
import ParentMessage from "../../../model/messages/messages";
import { MessageContent } from "../../../model/messages/messages";
import messageSample from "../../../model/messages/messageSample.json";


//for default props
const jsonString = JSON.stringify(messageSample);
const sampleMessages = JSON.parse(jsonString) as ParentMessage[];
sampleMessages[1].message.message[0].message="Hello, how can I help you today? This is some long text. This is some long text. This is some long text. This is some long text. This is some long text.  "
sampleMessages[0].message.message[0].message="Hello, how can I help you today? "

export default { component: ChatBotChat, title: "Elements/Chat/ChatBotChat" } as Meta;

export const ShortText = {
  args: {
    message: sampleMessages[0]
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
    message: sampleMessages[1]
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
