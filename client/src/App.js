// src/App.js
import React from 'react';
import { ThemeProvider } from '@mui/material/styles'; // Import ThemeProvider and createTheme
import ProtectedRoute from './routeAuth';
import { lightTheme } from './assets/theme';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import MainPage from './pages/home.tsx';

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

//<Navigate to="/index/chat" />
//<Route path="/index/*" element={<MainPage />} />
// add back <protected route>
const App = () => (
<ThemeProvider theme={lightTheme}>
    <Router>
      <Routes>
        <Route path="*" element={
          <MainPage />} />
      </Routes>
    </Router>
</ThemeProvider>
);

export default App;

