import React from 'react';
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { EventType } from "@azure/msal-browser";

const LoginButton = () => {

    const { instance, accounts, inProgress } = useMsal();

    const handleLogin = () => {
        // Account selection logic is app dependent. Adjust as needed for different use cases.
        // Set active acccount on page load
        const accounts = instance.getAllAccounts();
        if (accounts.length > 0) {
        instance.setActiveAccount(accounts[0]);
        }

        instance.addEventCallback((event) => {
        // set active account after redirect
        if (event.eventType === EventType.LOGIN_SUCCESS && event.payload.account) {
            console.log("login success")
            const account = event.payload.account;
            instance.setActiveAccount(account);
            console.log(account)
        }
        }, error=>{
        console.log('error', error);
        });

        console.log('get active account', instance.getActiveAccount());

        // handle auth redired/do all initial setup for msal
        instance.handleRedirectPromise().then(authResult=>{
        // Check if user signed in 
        const account = instance.getActiveAccount();
        if(!account){
            // redirect anonymous user to login page 
            console.log("there is no account...logging in")
            console.log(instance)
            instance.loginRedirect();
        }
        }).catch(err=>{
        // TODO: Handle errors
        console.log(err);
        });
    };

    return (
        <div >
            <button onClick={handleLogin}>
                Log In
            </button>
        </div>
    );
};

export default LoginButton;
