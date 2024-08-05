import { baseURL, endpointURL } from "./shared";

const logout = async () => {
    try {
        const response = await fetch(
            `${endpointURL}/oauth2/logout`, { method: "POST", credentials: "include" }
        )
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`)
        }
        const data = await response.json()
        window.location.href = `${baseURL}?logout=true`
    } catch (e) {
        console.log((e as Error).message)
    }

}

const validateAuth = async (): Promise<boolean> => {
    try {
        const response = await fetch(
            `${endpointURL}/oauth2/validate_auth_cookie`, {
            method: "POST",
            credentials: "include"
        },
        )
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const data = await response.json();
        return data.valid
    } catch (error) {
        console.error((error as Error).message)
        return false
    }
}

const getJWTToken = async (code: string): Promise<string> => {
    try {
        const response = await fetch(
            `${endpointURL}/oauth2/token`, {
            method: "POST",
            body: new URLSearchParams({
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": baseURL,
            }),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            credentials: "include",
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


const setToken = async (setAuthorized: (value: boolean | null) => void) => {
    const authValidated = await validateAuth();
    if (!authValidated) {
        const query = new URLSearchParams(window.location.search);
        const code = query.get("code");
        if (code) {
            await getJWTToken(code);
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.delete("code");
            window.history.replaceState({}, document.title, newUrl.toString());
            setAuthorized(true)
        } else {
            setAuthorized(false)
        }
    } else {
        setAuthorized(true)
    }
}


export { validateAuth, setToken, getJWTToken, logout };