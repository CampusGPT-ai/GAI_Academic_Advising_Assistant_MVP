import '@testing-library/jest-dom/extend-expect';
import { act, render, screen, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { composeStories } from '@storybook/testing-react';
import App from './App';


test('renders learn react link', () => {
  const results = render(<App />);
});
