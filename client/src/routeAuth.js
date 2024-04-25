import React from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { EventType } from "@azure/msal-browser";
import { useEffect } from "react";
import useSamlAuth from "./hooks/useSamlAuth";

export function SAMLProtectedRoute({ children }) {

    let isAuthenticated = false; // Replace with your auth logic
    if (localStorage.getItem("authToken")) {
        isAuthenticated = true; // Replace with your auth logic
    }
    console.log(`checking SAML login status for user.  user is authenticated? ${isAuthenticated}`)
    
    const samlLoginUrl = process.env.REACT_APP_LOGIN_URL; // THIS WILL BE UPDATED WITH THE ACTUAL SAML LOGIN URL
    console.log(`saml login url: ${samlLoginUrl}`);
    debugger;

    if (!isAuthenticated) {
        window.location.href = samlLoginUrl;
        return null;
    }

    return children;
}

export default function ProtectedRoute({children}) {
    const { instance, inProgress } = useMsal();
    const isAuthenticated = useIsAuthenticated();
    // console.log(`checking login status for user.  user is authenticated? ${isAuthenticated} login in progress?  ${inProgress} with instance ${JSON.stringify(instance)}`);
    



    instance.addEventCallback((event) => {
        // set active account after redirect
        if (event.eventType === EventType.LOGIN_SUCCESS && event.payload.account) {
            // console.log("login success")
            const account = event.payload.account;
            instance.setActiveAccount(account);
        }
        }, error=>{
        console.log('error', error);
        });

    // console.log(`checking login status for user.  user is authenticated? ${isAuthenticated} login in progress?  ${inProgress} with instance ${JSON.stringify(instance)}`)

    useEffect(() => {
        const authenticate = async () => {
            if (!isAuthenticated && inProgress === "none") {
                // console.log(`in progress: ${inProgress}`);
                // console.log(`is Authenticated: ${isAuthenticated}`);
                try {
                    // console.log(`initiating login for instance ${JSON.stringify(instance)}`);
                    await instance.loginRedirect(); // or loginPopup
                    // console.log(`checking state variables for isAuth: ${isAuthenticated} and inProgress: ${inProgress}`);
                } catch (e) {
                    console.error("Login failed:", e);
                }
            }
        };
    
        authenticate();
    
        return () => {
            // Cleanup if needed
        };
    }, [isAuthenticated, inProgress, instance]);
    


    // Render content conditionally based on the authentication status
    if (isAuthenticated) {
        // console.log(`returning auth status: ${isAuthenticated}`)
    // User is authenticated, render the protected content
    return (
        <div>
            {children} {/* Protected content */}
        </div>
            );
    } else if (inProgress !== InteractionStatus.None) {
        // Authentication or token acquisition is in progress
        return <div>Loading authentication...</div>;
    } else {
        // User is not authenticated, and no interaction is in progress
        // Optionally, render a message, a loading indicator or return null
        return <div>error loading authentication: </div>;
    }

}