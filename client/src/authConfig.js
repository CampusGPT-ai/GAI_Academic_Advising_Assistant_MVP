import { BaseUrl } from "./api/baseURL";

export const msalConfig = {
    auth: {
      clientId: 'YOUR_CLIENT_ID', // from Azure AD application
      authority: 'https://login.microsoftonline.com/YOUR_TENANT_ID',
      redirectUri: BaseUrl(), // or your React app's URL
    },
    cache: {
      cacheLocation: 'sessionStorage', // or 'localStorage'
      storeAuthStateInCookie: true, // recommended for browsers
    },
  };
  