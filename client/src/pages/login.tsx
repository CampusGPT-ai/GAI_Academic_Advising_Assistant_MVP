import React from 'react';
import { useMsal } from '@azure/msal-react';

function Login() {
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginRedirect({
      scopes: ['User.Read'] // Define scopes as needed
    }).catch(e => {
      console.error(e);
    });
  };

  return <button onClick={handleLogin}>Login</button>;
}

export default Login;
