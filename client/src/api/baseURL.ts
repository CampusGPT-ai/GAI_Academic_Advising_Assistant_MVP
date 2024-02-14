const DOMAIN = process.env.REACT_APP_DOMAIN || 'development';
const ENV = process.env.REACT_APP_WEBENV || 'development';
const CLIENT_BASE = process.env.REACT_APP_CLIENT_APP_NAME || 'http://localhost:3000';
const APP_BASE = process.env.REACT_APP_APP_NAME || 'http://localhost:8000';
export const BaseUrl = () => {
    console.log(`Base URL Domain: ${DOMAIN},Base URL environment: ${ENV}`)
    let BASE_URL = '';
    if (DOMAIN === 'development') {
      BASE_URL = `http://${APP_BASE}`;
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
      BASE_URL = `http://${CLIENT_BASE}`;
    } else {
      if (ENV === 'production') {
        BASE_URL = `https://${CLIENT_BASE}.azurewebsites.net`;
      } else {
        BASE_URL = `https://${CLIENT_BASE}-development.azurewebsites.net`;
      }
    }
    return BASE_URL;
  };
  
    
