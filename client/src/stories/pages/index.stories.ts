//src/stories/pages/index.stories.ts
import { Meta } from "@storybook/react";
import { userEvent, waitFor, within } from '@storybook/testing-library';
import { expect } from '@storybook/jest';
import MainPage from "../../pages/home";

  export default {
  component: MainPage,
  title: 'pages/home',
 } as Meta;
  export const Primary = { args: { primary: true } };

  const inputText = 'What is the application deadline?';

  export const NewChatTest = {
    play: async ({ canvasElement } : { canvasElement: any }) => {
      const canvas = within(canvasElement);

      const chatInput = canvas.getByRole('textbox');

      await userEvent.type(chatInput, inputText, {
        delay: 100,
      });
      await expect((chatInput as HTMLInputElement).value).toBe(inputText);
  
      const newChatButton = canvas.getByText(/New Chat/i);
  
      await waitFor(() => userEvent.click(newChatButton));
    },
  };