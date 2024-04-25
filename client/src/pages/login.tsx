import React, { FC } from "react";
import useSamlAuth from "../hooks/useSamlAuth";
const LoginPage: FC = () => {
    console.log('using saml auth')
    useSamlAuth() 
    return (<div>redirecting to login...</div>);}
export default LoginPage;