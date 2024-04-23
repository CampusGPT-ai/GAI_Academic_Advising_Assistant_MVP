import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { lightTheme } from './assets/theme';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import MainPage from './pages/home.tsx'; // Make sure this is the correct import
import MainPageGraph from './pages/home'; // Verify this too
import useSamlAuth from './hooks/useSamlAuth'; // Assuming this hook handles authentication logic
import ProtectedRoute, { SAMLProtectedRoute } from './routeAuth'; // Verify these imports

const authType = process.env.REACT_APP_AUTH_TYPE;
console.log(`auth type =`, authType);

function App() {
  useSamlAuth(); // Hook for handling authentication based on token presence

  return (
    <ThemeProvider theme={lightTheme}>
      <Router>
        <Routes>
          <Route path="*" element={
            authType === 'SAML' ? (
              <SAMLProtectedRoute>
                <MainPageGraph />
              </SAMLProtectedRoute>
            ) : authType === 'MSAL' ? (
              <ProtectedRoute>
                <MainPage />
              </ProtectedRoute>
            ) : (
              <MainPage />
            )
          } />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
