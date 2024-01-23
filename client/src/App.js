// src/App.js
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles'; // Import ThemeProvider and createTheme
import {lightTheme as theme} from './assets/theme';
import MainPage from './components/pages/home';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';


import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
//<Navigate to="/index/chat" />
//<Route path="/index/*" element={<MainPage />} />
const App = () => (
<ThemeProvider theme={theme}>
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/index/chat" />} />
        <Route path="/index/*" element={<MainPage />} />
      </Routes>
    </Router>
</ThemeProvider>
);

export default App;

