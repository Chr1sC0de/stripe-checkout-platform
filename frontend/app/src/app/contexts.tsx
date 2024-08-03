"use client"
import { createContext } from "react";


export type MyAppContextType = {
    page: string | null,
    setPage: (value: string | null) => void,
    authorized: boolean | null,
    setAuthorized: (value: boolean | null) => void,
    cart: { [id: string]: { [id: string]: string | number } | string | number } | {},
    setCart: (value: { [id: string]: { [sub_id: string]: any } } | {}) => void
}

export const AppContext = createContext<MyAppContextType>(
    {
        page: "Products",
        setPage: (value: string | null) => { value },
        authorized: false,
        setAuthorized: (value: boolean | null) => { value },
        cart: {},
        setCart: (value: { [id: string]: { [sub_id: string]: any } }) => { value }
    }
);

