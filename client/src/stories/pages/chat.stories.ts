//src/stories/pages/index.stories.ts
import { Meta } from "@storybook/react";
import Chat from "../../pages/chat";
import { userEvent, waitFor, within } from '@storybook/testing-library';
import { expect } from '@storybook/jest';
import * as ChatInputStories from "../elements/chat/chatInput.stories";
import AppStatus from "../../model/conversation/statusMessages";


export default { component: Chat,
  title: 'pages/chat',
  args: {...ChatInputStories.default.args},
} as Meta;

export const Primary = { args: { primary: true}};

const inputText = 'What is the application deadline?';

export const ChatAppStatusIdleButton = {
  args: {appStatus: AppStatus.Idle},
  play: async ({ canvasElement } : { canvasElement: any }) => {
    const canvas = within(canvasElement);

    const chatInput = canvas.getByRole('textbox');

    await userEvent.type(chatInput, inputText, {
      delay: 100,
    });
    await expect((chatInput as HTMLInputElement).value).toBe(inputText);

    const submitButton = canvas.getByRole('button');

    await waitFor(() => userEvent.click(submitButton));
  },
};

export const ChatAppStatusIdleKeyboard = {
  args: {appStatus: AppStatus.Idle},
  play: async ({ canvasElement } : { canvasElement: any }) => {
    const canvas = within(canvasElement);

    const chatInput = canvas.getByRole('textbox');

    await userEvent.type(chatInput, inputText, {
      delay: 100,
    });
    await expect((chatInput as HTMLInputElement).value).toBe(inputText);

    await userEvent.keyboard('{enter}');
  },
};

export const ChatAppStatusGettingMessageHistory = {
  args: {appStatus: AppStatus.GettingMessageHistory},
  play: async ({ canvasElement } : { canvasElement: any }) => {
    const canvas = within(canvasElement);

    const chatInput = canvas.getByRole('textbox');
    await expect((chatInput as HTMLInputElement).disabled).toBe(true);

    const submitButton = canvas.getByRole('button');
    await expect((submitButton as HTMLInputElement).disabled).toBe(true);
  },
};

export const ChatAppStatusGeneratingResponse = {
  args: {appStatus: AppStatus.GeneratingChatResponse},
  play: async ({ canvasElement } : { canvasElement: any }) => {
    const canvas = within(canvasElement);

    const chatInput = canvas.getByRole('textbox');
    await expect((chatInput as HTMLInputElement).disabled).toBe(true);

    const submitButton = canvas.getByRole('button');
    await expect((submitButton as HTMLInputElement).disabled).toBe(true);
  },
};

export const ChatAppStatusSavingConversation = {
  args: {appStatus: AppStatus.SavingConversation},
  play: async ({ canvasElement } : { canvasElement: any }) => {
    const canvas = within(canvasElement);

    const chatInput = canvas.getByRole('textbox');
    await expect((chatInput as HTMLInputElement).disabled).toBe(true);

    const submitButton = canvas.getByRole('button');
    await expect((submitButton as HTMLInputElement).disabled).toBe(true);
  },
};

export const ChatAppStatusError = {
  args: {appStatus: AppStatus.Error},
  play: async ({ canvasElement } : { canvasElement: any }) => {
    const canvas = within(canvasElement);

    const chatInput = canvas.getByRole('textbox');
    await expect((chatInput as HTMLInputElement).disabled).toBe(true);

    const submitButton = canvas.getByRole('button');
    await expect((submitButton as HTMLInputElement).disabled).toBe(true);
  },
};