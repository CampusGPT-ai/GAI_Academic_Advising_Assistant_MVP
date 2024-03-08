import React from 'react';
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { EventType } from "@azure/msal-browser";
import { useEffect } from "react";



export default function ProtectedRoute({children}) {
    const { instance, inProgress } = useMsal();
    const isAuthenticated = useIsAuthenticated();
    console.log(`checking login status for user.  user is authenticated? ${isAuthenticated} login in progress?  ${inProgress} with instance ${JSON.stringify(instance)}`);
    



    instance.addEventCallback((event) => {
        // set active account after redirect
        if (event.eventType === EventType.LOGIN_SUCCESS && event.payload.account) {
            console.log("login success")
            const account = event.payload.account;
            instance.setActiveAccount(account);
        }
        }, error=>{
        console.log('error', error);
        });

    // console.log(`checking login status for user.  user is authenticated? ${isAuthenticated} login in progress?  ${inProgress} with instance ${JSON.stringify(instance)}`)

    useEffect(() => {
        if (!isAuthenticated && inProgress === "none") {
            // Initiate login only if no other interaction is in progress
            // console.log(`initiating login for instance ${JSON.stringify(instance)}`);
            console.log(`in progress: ${inProgress}`)
            console.log(`is Authenticated: ${isAuthenticated}`)
            try {
                console.log(`initiating login for instance ${JSON.stringify(instance)}`);
                
                instance.loginRedirect(); // or loginPopup
                console.log(`checking state variables for isAuth: ${isAuthenticated} and inProgress: ${inProgress}`)
                debugger;
            } catch (e) {

                console.error("Login failed:", e);
                debugger;
                // Optionally, update state to show error message to the user
                // setError(e); // You would need to define `setError` and `error` state with `useState`
            }
        }
        return () => {
        };
    }, [isAuthenticated, inProgress, instance]);


    // Render content conditionally based on the authentication status
    if (isAuthenticated) {
        console.log(`returning auth status: ${isAuthenticated}`)
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