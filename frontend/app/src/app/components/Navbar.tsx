"use client"

import React, { useContext, useState } from 'react';
import Image from 'next/image';
import { AppContext } from '../contexts';
import { DialogBackdrop, Dialog, DialogPanel, DialogTitle } from '@headlessui/react'
import LoginButton from './LoginButton';
import { endpointURL, baseURL } from '../lib/shared';
import { logout } from '../lib/auth';

interface ActiveScreenProps {
    target: string;
}

const PageContextSwitcher: React.FC<ActiveScreenProps> = ({ target }) => {
    const { page, setPage } = useContext(AppContext);
    const clickHandler = () => {
        setPage(target);
    };
    return (
        <button type="button" onClick={clickHandler} className='text-lg'>
            <p className={page === target ? 'border-b-2 border-slate-200' : ''}>
                {target}
            </p>
        </button>
    );
};


const CompanyLogo = () => {
    return <div className="flex space-x-4 p-4 items-center font-bold text-2xl">
        <Image
            src="/company-logo.png"
            alt="Company Logo"
            width={85}
            height={85}
            priority
        />
        <p>Snack Mate</p>
    </div>
}

const Navbar: React.FC = () => {
    const [isLogoutOpen, setIsLogoutOpen] = useState(false);
    const [isCartOpen, setIsCartOpen] = useState(false)
    const appContext = useContext(AppContext);
    const cart: { [id: string]: { [id: string]: number } } = appContext.cart

    const cartCounter = (): number | null => {
        let content = 0
        for (let key in appContext.cart) {
            content += cart[key]["quantity"]
        }
        if (content == 0) {
            return null
        }
        return content
    }


    const checkout = async () => {
        const checkoutItems = []
        for (let k in cart) {
            checkoutItems.push({ price: cart[k]["price"], quantity: cart[k]["quantity"] })

        }
        const url = new URL('/stripe/create-checkout-session', endpointURL)
        url.searchParams.append("return_type", 'json')
        url.searchParams.append("success_url", `${baseURL}?success=true`)
        url.searchParams.append("cancel_url", `${baseURL}?cancel=true`)
        try {
            const response = await fetch(url.toString(), {
                method: "POST",
                body: JSON.stringify(checkoutItems),
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: "include"
            }
            )
            if (!response.ok) {
                throw new Error(`Response status: ${response.status}`);
            }
            const data = await response.json()
            window.location.href = data.url
        } catch (e) {
            console.log((e as Error).message)
        }

    }

    const handleLogout = () => {
        console.log("logging out")
        logout()
        console.log("finished logging out")
    }


    const handleCheckout = () => {
        if (!cartCounter()) {
            setIsCartOpen(true)
        } else {
            checkout()
        }
    }


    return (
        <nav className="top-0 left-0 w-full pb-4 pt-4 h-32 z-100 text-red-400 border mb-10">
            <div className="flex pl-12 pr-12 items-center justify-between w-full h-full">
                <CompanyLogo />
                <div className="flex h-full justify-center items-center space-x-5 pt-2 pb-2">
                    {
                        ["Products", "Popular", "Recent"].map(
                            (item) => (<PageContextSwitcher target={item} key={item} />)
                        )
                    }
                    {
                        appContext.authorized ? <button onClick={handleLogout} className="border p-2 rounded-md bg-slate-100 hover:bg-slate-200 text-lg">Logout</button> :
                            <>
                                <button onClick={() => setIsLogoutOpen(true)} className="border p-2 rounded-md bg-slate-100 hover:bg-slate-200 text-lg">Login</button>
                                <Dialog open={isLogoutOpen} onClose={() => setIsLogoutOpen(false)} transition className="fixed inset-0 w-screen flex items-center justify-center bg-black/30 p-4 transition duration-300 ease-out data-[closed]:opacity-0">
                                    <DialogBackdrop className="fixed inset-0 bg-black/30" />
                                    <div className="fixed inset-0 flex w-screen items-center justify-center p-4 ">
                                        <DialogPanel className="flex flex-col justify-center relative w-2/6 h-3/6 border rounded-xl bg-white p-12">
                                            <button onClick={() => setIsLogoutOpen(false)} className='absolute top-1 right-1 m-2 text-gray-800 hover:text-gray-500 focus:outline-none'>X</button>
                                            <div className='flex flex-col items-center  w-full  space-y-2 divide-y-2'>
                                                <DialogTitle className="font-bold">Login</DialogTitle>
                                                <div className='w-full pt-3'>
                                                    <LoginButton provider='Facebook' className='p-2 w-full bg-cyan-700 hover:bg-cyan-800 text-white rounded-2xl' />
                                                </div>
                                            </div>
                                        </DialogPanel>
                                    </div>
                                </Dialog>
                            </>
                    }
                    <div className="relative flex flex-col justify-center items-center border bg-red-300 w-10 h-10 m-auto">
                        <button onClick={() => handleCheckout()} type='button' className="border p-2 rounded-md bg-slate-100 hover:bg-slate-200 text-lg">Order</button>
                        <p className='absolute -top-4 -right-4 text-green-500'>{cartCounter()}</p>
                        <Dialog open={isCartOpen} onClose={() => setIsCartOpen(false)} transition className="fixed inset-0 w-screen flex items-center justify-center bg-black/30 p-4 transition duration-300 ease-out data-[closed]:opacity-0">
                            <div className="fixed inset-0 flex w-screen items-center justify-center p-4 ">
                                <DialogPanel className="relative  border rounded-xl bg-white p-12">
                                    <button onClick={() => setIsCartOpen(false)} className='absolute top-1 right-1 m-2 text-gray-800 hover:text-gray-500 focus:outline-none'>X</button>
                                    <div className='flex flex-col items-center  w-full  space-y-2 divide-y-2'>
                                        <DialogTitle className="font-bold">Nothing in le cart</DialogTitle>
                                    </div>
                                </DialogPanel>
                            </div>
                        </Dialog>
                    </div>
                </div>
            </div>
        </nav >
    );
};

export default Navbar;