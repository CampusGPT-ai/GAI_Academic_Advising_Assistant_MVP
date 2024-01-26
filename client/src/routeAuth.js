import React from 'react';
import { useIsAuthenticated } from '@azure/msal-react';
import { Navigate } from 'react-router-dom'; // assuming you are using react-router

const ProtectedRoute = ({ children }) => {
    const isAuthenticated = useIsAuthenticated();

    if (!isAuthenticated) {
        // Redirect them to the login page, but save the current location they were
        // trying to go to when they were redirected. This allows us to send them
        // along to that page after they login, which is a nicer user experience
        // than dropping them off on the home page.
        return <Navigate to="/login" />;
    }

    return children;
};

export default ProtectedRoute;