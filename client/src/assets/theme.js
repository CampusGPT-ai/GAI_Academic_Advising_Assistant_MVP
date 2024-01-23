import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import { createTheme } from '@mui/material';
import { blueGrey, cyan, pink } from '@mui/material/colors';


export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      light: '#FEF9E0',
      mid: '#FBE680',
      main: '#F7CC00',
      dark: '#F1AD00 ',
      contrastText: '#000000',
      darkText: '#ffffff',
    },
    secondary: {
      light: '#000000',
      main: '#F1AD00',
      dark: '#000000',
      contrastText: '#F7CC00',
    },
    warning: {
      main: '#ba1a1a',
    },
    info: {
      main: '#ffddbb',
    },
    success: {
      main: '#b3bc52',
    },
    text: {
      primary: '#F1AD00',
      secondary: '#000',
  },
},
  typography: {
    variantMapping: {
      h1: 'h2',
      h2: 'h2',
      h3: 'h2',
      h4: 'h2',
      h5: 'h2',
      h6: 'h2',
      subtitle1: 'h2',
      subtitle2: 'h2',
      body1: 'span',
      body2: 'span',
    },
    fontWeightLight: 200,
    fontWeightRegular: 400,
    fontWeightMedium: 600,
    fontWeightBold: 800,
    button: {
      fontWeight: 500,
      lineHeight: 2,
    },
    h1: {
      fontSize: '2rem', // Adjust as needed
      fontWeight: 'bold', // Adjust as needed
      color: '#515abb', // Adjust as needed
    },
    h2: {
      fontSize: '1.5rem', // Adjust as needed
      fontWeight: 400, // Adjust as needed
      color: '#000', // Adjust as needed
    },
    h6: {
      fontSize: '1rem', // Adjust as needed
      color: '#F1AD00', // Adjust as needed
    }
  },
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: pink['A200'],
    },
    secondary: {
      main: cyan['A400'],
    },
    background: {
      default: blueGrey['800'],
      paper: blueGrey['700'],
    },
  },
});

