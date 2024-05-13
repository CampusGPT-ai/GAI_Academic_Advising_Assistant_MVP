import React, { useRef } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { EventType } from "@azure/msal-browser";
import { useEffect } from "react";
import useSamlAuth from "./hooks/useSamlAuth";

export function SAMLProtectedRoute({ children }) {

    let isAuthenticated = false; 
    if (localStorage.getItem("authToken")) {
        isAuthenticated = true; 
    }
    console.log(`checking SAML login status for user.  user is authenticated? ${isAuthenticated}`)
    
    const samlLoginUrl = 
    process.env.REACT_APP_DOMAIN !== "development" ? 
        `https://${process.env.REACT_APP_APP_NAME}-${process.env.REACT_APP_WEBENV}.azurewebsites.net/saml/login` : 
        `http://localhost:8000/saml/login`;

    console.log(`saml login url: ${samlLoginUrl}`);
    //debugger;

    if (!isAuthenticated) {
        console.log("redirecting to SAML login page");
        window.location.href = samlLoginUrl;
    }

    return children;
}

export default function ProtectedRoute({children}) {
    const { instance, inProgress } = useMsal();
    const isAuthenticated = useIsAuthenticated();
    const statusRef = useRef(inProgress);




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

    //console.log(`checking MSAL login status for user.  user is authenticated? ${isAuthenticated} login in progress?  ${inProgress} with instance ${JSON.stringify(instance)}`);
    //debugger;
    useEffect(() => {
        //console.log(`detected change to user login status.  user is authenticated? ${isAuthenticated} login in progress?  ${inProgress}}`);
        //debugger;
        const authenticate = async () => {
            if (!isAuthenticated && inProgress === "none") {

                try {
                    console.log(`initiating MSAL Login with redirect `);
                   //debugger;
                    await instance.loginRedirect(); // or loginPopup
                    console.log(`checking state variables for isAuth: ${isAuthenticated} and inProgress: ${inProgress}`);
                    //debugger;
                } catch (e) {
                    console.error("Login failed:", e);
                    debugger;   
                }
            }
        };
        
        if (!isAuthenticated && inProgress === InteractionStatus.None && inProgress !== statusRef.current) {
            console.log(`auth status changed from ${statusRef.current} to ${inProgress}, running authenticate function`)
            //debugger;
            statusRef.current = inProgress;
            authenticate();
        }
    
        return () => {
            // Cleanup if needed
        };
    }, [isAuthenticated, inProgress, instance]);
    


    // Render content conditionally based on the authentication status
    if (isAuthenticated) {
    // User is authenticated, render the protected content
    return (
        <div>
            {children} {/* Protected content */}
        </div>
            );
    } else if (inProgress !== InteractionStatus.None) {
        // Authentication or token acquisition is in progress
        //console.log(`returning auth status: ${isAuthenticated}`)
        //debugger;
        return <div>Loading authentication...</div>;
    } else {
        // User is not authenticated, and no interaction is in progress
        // Optionally, render a message, a loading indicator or return null
        return <div>Loading authentication...</div>;
    }

}