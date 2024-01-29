import React from 'react';
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { useEffect, useState } from "react";
import sendTokenToBackend from './api/validateToken';

export default function ProtectedRoute({children}) {
    const { instance, accounts, inProgress } = useMsal();
    const [sessionId, getSessionId] = useState();
    const isAuthenticated = useIsAuthenticated();
    // console.log(`checking login status for user.  user is authenticated? ${isAuthenticated} login in progress?  ${inProgress} with instance ${JSON.stringify(instance)}`)

    useEffect(() => {
        if (!isAuthenticated && inProgress === InteractionStatus.None) {
            // Initiate login only if no other interaction is in progress
            console.log(`initiating login for instance ${JSON.stringify(instance)}`);
            instance.loginRedirect(); // or loginPopup
        }
    }, [isAuthenticated, inProgress, instance]);
    

    useEffect(() => {
        if (accounts.length > 0 && inProgress === "none") {
            console.log(`sending token to backend for ${JSON.stringify(accounts[0].username)}`)
            getSessionId(sendTokenToBackend(accounts[0], instance));
        }
    },[accounts, inProgress])

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
        return <div>Loading authentication...</div>;
    } else {
        // User is not authenticated, and no interaction is in progress
        // Optionally, render a message, a loading indicator or return null
        return <div>Please wait...</div>;
    }

}