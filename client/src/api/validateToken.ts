import React from 'react';
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { BaseUrl } from './baseURL';
interface BackendResponse {
    user_id?: string;
    session_id?: string;
    account?: string;
    instance: any,
}

const sendTokenToBackend = async(account: AccountInfo, instance: IPublicClientApplication) => {

        const endpoint = `${BaseUrl()}/validate_token`;

        // Acquire token silently or interactively based on your requirement
        try {
           const token = process.env.REACT_APP_LOCAL_DEV_TOKEN;
            if (process.env.REACT_APP_DOMAIN !== 'development') {
                const response = await instance.acquireTokenSilent({
                    scopes: ['828d30c9-9619-4a12-8604-96d44653958f/.default'], // Use .default alone
                    account: account,
                });


                const token: string = response.accessToken;
            };
            console.log(`Got token from login: ${token}`);

            // Send the token to your backend
            const backendResponse = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },

            });

            if (!backendResponse.ok) {
                // Handle the scenario where the token is not valid
                console.error('Token validation failed');
                // Handle error, redirect to login or show an error message
            } else {
                // Token is valid, user is considered logged in on the server
                console.log('User logged in successfully');
                const data: BackendResponse = await backendResponse.json();
                console.log(`Received user data from backend response ${JSON.stringify(data)}`)
                return data.session_id
                // You can perform further actions here if needed
            }
        } catch (error: any) {
            if (error.name === 'InteractionRequiredAuthError') {
                await instance.acquireTokenRedirect({
                    scopes: ['User.Read'],
                    account: account,
                });
            } else {
                console.error(error);
            }
        }
    }
;

// Use this function inside a React component or hook
export default sendTokenToBackend;
