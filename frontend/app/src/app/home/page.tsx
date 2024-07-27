"use client"
import { useState, useEffect } from 'react'

// const endpointURL = "https://mtf4pr35a6mqcoxdviotpsyvbu0nbtxm.lambda-url.ap-southeast-2.on.aws"

// const getUserDetails = async (): Promise<any> => {
//     try {
//         const response = await fetch(`${endpointURL}/user`, {
//             method: "GET",
//             credentials: 'include',
//         })
//         if (!response.ok) {
//             throw new Error(`Response status: ${response.status}`);
//         }
//         const data = await response.json()
//         console.log(data)
//         return data

//     } catch (error) {
//         console.log((error as Error).message)
//         return ""
//     }
// }

export function User() {
    // const [data, setData] = useState(null)
    // const [isLoading, setLoading] = useState(true)

    // useEffect(() => {
    //     const fetchUserData = async () => {
    //         const userData = await getUserDetails()
    //         if (userData) {
    //             setData(userData)
    //             setLoading(false)
    //             console.log(userData)
    //         }

    //     }
    //     fetchUserData()

    // }, [])


    // if (isLoading) return <p>Loading...</p>
    // if (!data) return <p>No profile data</p>

    return (
        <div className="flex min-h-screen flex-col items-center justify-between p-20">

            {/* <p>Welcome, {data.UserAttributes[0].Value}</p> */}
            <p>hello world</p>

        </div >
    )
}



export default User