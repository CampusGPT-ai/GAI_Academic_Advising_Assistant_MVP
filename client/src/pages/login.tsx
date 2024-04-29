import React, { FC } from "react";
import useSamlAuth from "../hooks/useSamlAuth";

const authType = process.env.REACT_APP_AUTH_TYPE;

const LoginPage: FC = () => {
    console.log('using saml auth')
    debugger;
    useSamlAuth() 
    return (<div>redirecting to login...</div>);}
export default LoginPage;