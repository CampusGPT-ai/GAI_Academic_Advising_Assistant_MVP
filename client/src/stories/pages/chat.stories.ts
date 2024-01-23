//src/stories/pages/index.stories.ts
import { Meta } from "@storybook/react";
import Chat from "../../components/pages/chat";


  export default { component: Chat,
  title: 'pages/chat'} as Meta;
  export const Primary = { args: { primary: true } };