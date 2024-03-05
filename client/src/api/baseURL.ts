const DOMAIN = process.env.REACT_APP_DOMAIN || 'production';
const ENV = process.env.REACT_APP_WEBENV || 'development';
const BASE = process.env.REACT_APP_CLIENT_APP_NAME || 'http://localhost:5000';
const APP_BASE = process.env.REACT_APP_APP_NAME || 'http://localhost:8000';
export const BaseUrl = () => {
    console.log(`Base URL Domain: ${DOMAIN},Base URL environment: ${ENV}`)
    debugger;
    let BASE_URL = '';
    if (DOMAIN === 'development') {
      BASE_URL = 'http://127.0.0.1:8000';
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
      BASE_URL = 'http://localhost:3000';
    } else {
      if (ENV === 'production') {
        BASE_URL = `https://${BASE}.azurewebsites.net`;
      } else {
        BASE_URL = `https://${BASE}-development.azurewebsites.net`;
      }
    }
    return BASE_URL;
  };
  
    
