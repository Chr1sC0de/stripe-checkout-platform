"use client"
import { cookies } from 'next/headers'
import { useState, useEffect } from 'react'

const endpointURL = "https://0.0.0.0:8000"
const redirectURI = "https://0.0.0.0:3000"

const getUserDetails = async (): Promise<any> => {
    try {
        const response = await fetch(`${endpointURL}/user`, {
            method: "GET",
            credentials: 'include',
        })
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const data = await response.json()
        console.log(data)
        return data

    } catch (error) {
        console.log((error as Error).message)
        return ""
    }
}
export function User() {
    const [data, setData] = useState(null)
    const [isLoading, setLoading] = useState(true)

    useEffect(() => {
        const fetchUserData = async () => {
            const userData = await getUserDetails()
            if (userData) {
                setData(userData)
                setLoading(false)
                console.log(userData)
            }

        }
        fetchUserData()

    }, [])


    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    return (
        <div className="flex min-h-screen flex-col items-center justify-between p-20">
            <p>Welcome, {data.UserAttributes[0].Value}</p>
        </div >
    )
}



export default User