import { RedirectUrl } from "./api/baseURL";


console.log(`redirect url: ${RedirectUrl()}, tenant: ${process.env.REACT_APP_MSAL_TENANT}, client: ${process.env.REACT_APP_MSAL_CLIENT}`);


export const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_MSAL_CLIENT,
    //authority: `https://login.microsoftonline.com/25614ce5-0ba2-49d6-aad1-facc0ca94d15/saml2`,
    //redirectUri: `https://nodee6xms76htorcw-development.azurewebsites.net/.auth/login/aad/callback`,
    authority: `https://login.microsoftonline.com/${process.env.REACT_APP_MSAL_TENANT}`,
    redirectUri: RedirectUrl(),
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: true,
  }
};
