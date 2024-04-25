import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function useSamlAuth() {
    let navigate = useNavigate();
    console.log('useSamlAuth');
    debugger;
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token'); // Assuming token is passed as a query parameter

        if (token) {
            localStorage.setItem('authToken', token);
            
        }
        navigate('/app'); // Redirect to the home page
    },);
}