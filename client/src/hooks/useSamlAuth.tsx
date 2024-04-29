import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const authType = process.env.REACT_APP_AUTH_TYPE;


export default function useSamlAuth() {
    let navigate = useNavigate();
    authType==="SAML" && console.log('useSamlAuth');
    useEffect(() => {
        if (authType !== "SAML") {
            console.log('auth type is not SAML, redirecting to /app')
            navigate('/app');
        }
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token'); // Assuming token is passed as a query parameter

        if (token) {
            console.log('setting token to local storage', token)
            localStorage.setItem('authToken', token);
        }
        navigate('/app'); // Redirect to the home page
    },);
}
