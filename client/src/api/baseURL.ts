const DOMAIN = process.env.REACT_APP_DOMAIN || 'development';
const ENV = process.env.REACT_APP_WEBENV || 'development';
const CLIENT_BASE = process.env.REACT_APP_CLIENT_APP_NAME || 'http://localhost:3000';
const APP_BASE = process.env.REACT_APP_APP_NAME || 'http://localhost:8000';
const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';
export const BaseUrl = () => {
    // console.log(`Base URL Domain: ${DOMAIN},Base URL environment: ${ENV}`)
    
    let BASE_URL = '';
    if (DOMAIN === 'development') {
      BASE_URL = `http://localhost:8000`;
    }  else {
      if (ENV === 'production') {
        BASE_URL = `https://${APP_BASE}.azurewebsites.net`;
      } else {
        BASE_URL = `https://${APP_BASE}-development.azurewebsites.net`;
      }
    }
    return BASE_URL;
  };
  

export const RedirectUrl = () => {
    // console.log(`Base URL Domain: ${DOMAIN},Base URL environment: ${ENV}`)
    let BASE_URL = '';
    if (DOMAIN === 'development') {
      BASE_URL = `http://localhost:3000`;
    } else {
      if (ENV === 'production') {
        BASE_URL = `https://${CLIENT_BASE}.azurewebsites.net`;
      } else {
        BASE_URL = `https://${CLIENT_BASE}-development.azurewebsites.net`;
      }
    }
    return BASE_URL;
  };
  
    
