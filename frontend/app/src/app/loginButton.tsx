"use client"
import { exec } from "child_process"
import { error } from "console"
import { useEffect, useRef, useState } from "react"
import React from "react"

const endpointURL = "https://0.0.0.0:8000"
const redirectURI = "https://0.0.0.0:3000"

const getJWTToken = async (code: string): Promise<string> => {
    try {
        const response = await fetch(
            `${endpointURL}/oauth2/token`, {
            method: "POST",
            body: new URLSearchParams({
                "grant_type": 'authorization_code',
                "code": code,
                "redirect_uri": redirectURI
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const data = await response.json();
        return data.access_token;
    } catch (error) {
        console.error((error as Error).message);
        return ""
    }
}


interface LoginButtonProps {
    provider: string,
    className: string
}

const LoginButton: React.FC<LoginButtonProps> = ({ provider, className }) => {
    const [token, setToken] = useState("")
    const [message, setMessage] = useState("")
    const effectRan = useRef(false);
    const renderCount = useRef(0);

    useEffect(() => {

        const fetchToken = async () => {
            const query = new URLSearchParams(window.location.search);
            const code = query.get('code');
            if (code) {
                const _jwtToken = await getJWTToken(code);
                setToken(_jwtToken);

                // Clear the code from the URL
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.delete('code');
                window.history.replaceState({}, document.title, newUrl.toString());
            }
        }
        const fetchMessage = async () => {
            const yehBoi = await getYeahBoi()
            setMessage(yehBoi)
        }
        if (!effectRan.current) {
            effectRan.current = true
            fetchToken();
            fetchMessage();
            renderCount.current += 1;
        }
    }, []);


    const handleState = () => {
        const searchParams = new URLSearchParams({
            identity_provider: `${provider}`,
            redirect_uri: redirectURI
        });
        window.location.href = `${endpointURL}/oauth2/authorize?${searchParams.toString()}`;
    }

    return (
        <div className="mt-4">
            {!token ?
                <button
                    className={className}
                    onClick={handleState}
                >{provider} SSO
                </button> : <p>{message}</p>
            }
        </div>
    )
}

export default LoginButton;