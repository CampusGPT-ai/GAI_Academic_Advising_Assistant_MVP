import React from 'react';
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { BaseUrl } from './baseURL';
interface BackendResponse {
    user_id?: string;
    session_id?: string;
    account?: string;
    instance: any,
}
const AUTH_TYPE = process.env.REACT_APP_AUTH_TYPE || 'NONE';

interface tokenData {
    accounts?: any;
    isAuthenticated?: boolean;
    inProgress?: string;
    instance?: IPublicClientApplication;

}

const sendTokenToBackend = async( {accounts, isAuthenticated, inProgress, instance} : tokenData ) => {


        let backendResponse: Response = new Response();
        // Acquire token silently or interactively based on your requirement
        try {
            if (AUTH_TYPE === 'MSAL')
            { 
                // console.log('Using MSAL for token validation')
                const account = accounts[0];
        
                if ( isAuthenticated && inProgress === 'none' && instance) {

                    const response = await instance.acquireTokenSilent({
                        scopes: ['828d30c9-9619-4a12-8604-96d44653958f/.default'], // Use .default alone
                        account: account,
                    });
                    
        
                    const token: string = response.accessToken;

                    backendResponse = await fetch(`${BaseUrl()}/validate_token`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
    
                });
            };
            }
            else {
                backendResponse = await fetch(`${BaseUrl()}/get_generic_token`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
            }
            
            // console.log(`Backend response recieved from server: ${backendResponse}`)
            if (!backendResponse.ok) {
                // Handle the scenario where the token is not valid
                console.error('Token validation failed');
                // Handle error, redirect to login or show an error message
            } else {
                // Token is valid, user is considered logged in on the server
                // console.log('User logged in successfully');
                const data: BackendResponse = await backendResponse.json();
                // console.log(`Received user data from backend response ${JSON.stringify(data)}`)
                return data.session_id
                // You can perform further actions here if needed
            }
        } catch (error: any) {
                console.error(error);
                throw error;
            }
        }
;

// Use this function inside a React component or hook
export default sendTokenToBackend;
