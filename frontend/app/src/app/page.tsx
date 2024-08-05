"use client"
import { AppContext } from './contexts';
import { useState } from "react";
import { useEffect } from "react";
import Navbar from './components/Navbar';
import { Transition } from "@headlessui/react"
import { useRef } from 'react';
import { logout, setToken, validateAuth } from './lib/auth';
import Products from './components/Products';
import Popular from './components/Popular';
import Recent from './components/Recent';


export default function Home() {
  const [cart, setCart] = useState<{} | { [id: string]: { [sub_id: string]: any } | {} }>({});
  const [page, setPage] = useState<string | null>("Products");
  const [authorized, setAuthorized] = useState<boolean | null>(null);
  const [logOutSuccessful, setLogoutSuccessful] = useState<boolean | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const effectRan = useRef(false);

  const pageContext = { page, setPage, authorized, setAuthorized, cart, setCart };


  useEffect(
    () => {
      const setValidateAuth = async () => {
        const valid = await validateAuth()
        setAuthorized(valid)
        if (!valid) {
          logout()
        }
      }

      if (!effectRan.current) {
        if (!authorized || (authorized === null)) {
          effectRan.current = true;
          setToken(setAuthorized);
        } else {
          setValidateAuth()
        }
      }
      setIsMounted(true)
      const savedPage = localStorage.getItem('currentPage');

      if (savedPage) {
        setPage(savedPage);
      }


    }, []
  )

  useEffect(() => {
    const newUrl = new URL(window.location.href);
    const checkLogoutSuccessful = newUrl.searchParams.get("logout")
    if (checkLogoutSuccessful) {
      setLogoutSuccessful(true)
    } else {
      setLogoutSuccessful(false)
    }
  })

  console.log(`Check Logout Successful ${logOutSuccessful}`)


  useEffect(() => {
    if (isMounted && page != null) {
      localStorage.setItem('currentPage', page);
    }
  }, [page, isMounted]);

  return (
    <AppContext.Provider value={pageContext}>
      <Transition show={isMounted && (authorized !== null)}>
        <div className='transition h-screen duration-300 ease-in data-[closed]:opacity-0'>
          <Navbar />
          <main className="flex flex-col h-fill min-h-96 items-center justify-center p-4 md:p-4">
            {
              (pageContext.page === "Products") ? <Products /> :
                (pageContext.page === "Popular") ? <Popular /> : <Recent />
            }
          </main >
        </div>
      </Transition>
    </AppContext.Provider>
  );
}
