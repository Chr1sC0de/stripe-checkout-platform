"use client"
import { createContext } from "react";


export const AppContext = createContext<{
    page: string | null,
    setPage: (value: string | null) => void,
    authorized: boolean | null,
    setAuthorized: (value: boolean | null) => void,
    cart: { [id: string]: { [sub_id: string]: any } } | {},
    setCart: (value: { [id: string]: { [sub_id: string]: any } } | {}) => void
}>(
    {
        page: "Products",
        setPage: (value: string | null) => { value },
        authorized: false,
        setAuthorized: (value: boolean | null) => { value },
        cart: {},
        setCart: (value: { [id: string]: { [sub_id: string]: any } }) => { value }
    }
);

