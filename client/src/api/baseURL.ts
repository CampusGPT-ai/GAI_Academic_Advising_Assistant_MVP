const DOMAIN = process.env.REACT_APP_DOMAIN || 'production';
const ENV = process.env.REACT_APP_WEBENV || 'development';

export const BaseUrl = () => {
    console.log(`Base URL Domain: ${DOMAIN},Base URL environment: ${ENV}`)
    let BASE_URL = '';
    if (DOMAIN === 'development') {
      BASE_URL = 'http://127.0.0.1:8000';
    } else {
      if (ENV === 'production') {
        BASE_URL = 'https://pythongnoba4quzzn5u.azurewebsites.net';
      } else {
        BASE_URL = 'https://pythongnoba4quzzn5u-development.azurewebsites.net';
      }
    }
    return BASE_URL;
  };
  
  