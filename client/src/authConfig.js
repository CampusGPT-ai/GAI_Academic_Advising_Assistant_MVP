import { RedirectUrl } from "./api/baseURL";



export const msalConfig = {
    auth: {
      clientId: process.env.REACT_APP_MSAL_CLIENT, // from Azure AD application
      authority: `https://login.microsoftonline.com/${process.env.REACT_APP_MSAL_TENANT}`,
      redirectUri: RedirectUrl(), // or your React app's URL
    },
    cache: {
      cacheLocation: 'sessionStorage', // or 'localStorage'
      storeAuthStateInCookie: true, // recommended for browsers
    },
  };
  