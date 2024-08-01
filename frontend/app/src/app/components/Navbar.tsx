"use client"

import React, { useContext, useEffect, useState } from 'react';
import Image from 'next/image';
import { AppContext } from '../contexts';
import { DialogBackdrop, Dialog, DialogPanel, DialogTitle } from '@headlessui/react'
import LoginButton from './LoginButton';

interface ActiveScreenProps {
    target: string;
}

const PageContextSwitcher: React.FC<ActiveScreenProps> = ({ target }) => {
    const { page, setPage } = useContext(AppContext);

    const clickHandler = () => {
        setPage(target);
    };

    return (
        <button type="button" onClick={clickHandler}>
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
    const [isOpen, setIsOpen] = useState(false);
    const appContext = useContext(AppContext);
    const cart: {
        [product_id: string]: { [quantity: string]: number }
    } = appContext.cart
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

    return (
        <nav className="top-0 left-0 w-full pb-4 pt-4 h-32 z-100 text-red-400">
            <div className="flex pl-12 pr-12 items-center justify-between w-full h-full">
                <CompanyLogo />
                <div className="flex h-full space-x-5 pt-2 pb-2 text-xl">
                    {
                        ["Products", "Popular", "Recent"].map(
                            (item) => (<PageContextSwitcher target={item} key={item} />)
                        )
                    }
                    {
                        appContext.authorized ? <button onClick={() => { }} className="border p-2 rounded-md bg-slate-100 hover:bg-slate-200">Logout</button> :
                            <>
                                <button onClick={() => setIsOpen(true)} className="border p-2 rounded-md bg-slate-100 hover:bg-slate-200">Login</button>
                                <Dialog open={isOpen} onClose={() => setIsOpen(false)} transition className="fixed inset-0 flex w-screen items-center justify-center bg-black/30 p-4 transition duration-300 ease-out data-[closed]:opacity-0">
                                    <DialogBackdrop className="fixed inset-0 bg-black/30" />
                                    <div className="fixed inset-0 flex w-screen items-center justify-center p-4 ">
                                        <DialogPanel className="relative w-2/6 h-3/5 border rounded-xl bg-white p-12">
                                            <button onClick={() => setIsOpen(false)} className='absolute top-1 right-1 m-2 text-gray-800 hover:text-gray-500 focus:outline-none'>X</button>
                                            <div className='flex flex-col items-center h-full w-full space-y-2 divide-y-2'>
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
                        <p className='absolute -top-4 -right-2 text-green-500'>{cartCounter()}</p>
                    </div>
                </div>
            </div>
        </nav >
    );
};

export default Navbar;