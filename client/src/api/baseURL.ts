const DOMAIN = process.env.REACT_APP_DOMAIN || 'production';
const ENV = process.env.REACT_APP_WEBENV || 'development';

export const BaseUrl = () => {
    console.log(`Base URL Domain: ${DOMAIN},Base URL environment: ${ENV}`)
    let BASE_URL = '';
    if (DOMAIN === 'development') {
      BASE_URL = 'http://127.0.0.1:80';
    } else {
      if (ENV === 'production') {
        BASE_URL = 'https://ce-demo-app.azurewebsites.net';
      } else {
        BASE_URL = 'https://ce-demo-app-dev.azurewebsites.net';
      }
    }
    return BASE_URL;
  };
  
  