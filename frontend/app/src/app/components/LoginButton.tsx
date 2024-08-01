"use client"
import React from "react"
import { endpointURL, baseURL } from "../lib/shared"

interface LoginButtonInterface {
    provider: string,
    className: string
}

const LoginButton: React.FC<LoginButtonInterface> = ({ provider, className }) => {

    const handleState = () => {
        const searchParams = new URLSearchParams({
            identity_provider: `${provider}`,
            redirect_uri: baseURL
        });
        window.location.href = `${endpointURL}/oauth2/authorize?${searchParams.toString()}`;
    }


    return (
        <button
            className={className}
            onClick={handleState}
        >{provider}
        </button>
    )
}

export default LoginButton;