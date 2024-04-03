import React from "react";
import { RedirectUrl } from "./api/baseURL";
import { redirect } from "react-router-dom";

console.log( `redirect url set to: ${RedirectUrl()} for domain ${process.env.REACT_APP_DOMAIN}`)
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
  