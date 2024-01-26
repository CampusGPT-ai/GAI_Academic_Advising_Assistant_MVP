import { Meta } from "@storybook/react";
import ChatCitation from "../../../components/chat/chatResponse/chatResponseElements/chatCitation";


export default { component: ChatCitation, title: "Elements/Chat/ChatCitation" } as Meta;

export const ShortText = {
  args: {
    text: "Hello, how can I help you today?"
  }
};

export const LongText = {
  args: {
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, sapien vel bibendum lacinia, velit velit bibendum sapien, vel bibendum sapien velit bibendum sapien."
  }
};


