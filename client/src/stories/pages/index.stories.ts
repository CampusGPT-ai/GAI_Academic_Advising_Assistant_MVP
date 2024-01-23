//src/stories/pages/index.stories.ts
import { Meta } from "@storybook/react";
import MainPage from "../../components/pages/home";


  export default { component: MainPage
  ,title: 'pages/home' } as Meta;
  export const Primary = { args: { primary: true } };