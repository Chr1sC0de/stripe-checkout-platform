"use client"
import { useEffect, useRef } from "react"
import React from "react"

const endpointURL = "https://mtf4pr35a6mqcoxdviotpsyvbu0nbtxm.lambda-url.ap-southeast-2.on.aws"
const baseURL = "https://0.0.0.0:3000"

const getJWTToken = async (code: string): Promise<string> => {
    try {
        const response = await fetch(
            `${endpointURL}/oauth2/token`, {
            method: "POST",
            body: new URLSearchParams({
                "grant_type": 'authorization_code',
                "code": code,
                "redirect_uri": baseURL,
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
        return "";
    }
}


interface LoginButtonProps {
    provider: string,
    className: string
}

const LoginButton: React.FC<LoginButtonProps> = ({ provider, className }) => {
    const effectRan = useRef(false);

    useEffect(() => {

        const fetchToken = async () => {
            const query = new URLSearchParams(window.location.search);
            const code = query.get('code');
            if (code) {
                const token = await getJWTToken(code);
                if (token) {
                    // Clear the code from the URL
                    const newUrl = new URL(window.location.href);
                    newUrl.searchParams.delete('code');
                    window.history.replaceState({}, document.title, newUrl.toString());

                    window.location.href = `${baseURL}/home`;
                }
            }
        }

        if (!effectRan.current) {
            effectRan.current = true;
            fetchToken();
        }
    }, []);

    const handleState = () => {
        const searchParams = new URLSearchParams({
            identity_provider: `${provider}`,
            redirect_uri: baseURL
        });
        window.location.href = `${endpointURL}/oauth2/authorize?${searchParams.toString()}`;
    }

    return (
        <div className="mt-4">
            <button
                className={className}
                onClick={handleState}
            >{provider} SSO
            </button>
        </div>
    )
}

export default LoginButton;