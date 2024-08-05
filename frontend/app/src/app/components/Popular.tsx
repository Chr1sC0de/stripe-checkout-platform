"use client"
import { endpointURL } from "../lib/shared"
import { useState } from "react"
import { useEffect } from "react"
import { Transition } from "@headlessui/react";
import { MoonLoader } from "react-spinners";

const getPopularity = async (setItemPopularity: CallableFunction) => {
    try {
        const response = await fetch(
            `${endpointURL}/stripe/product-popularity`, {
            method: "GET"
        }
        )
        if (!response.ok) {
            throw new Error(`Response Status: ${response.status}`)
        }
        const data = await response.json()
        setItemPopularity(data)

    } catch (e) {
        throw (e as Error).message
    }

}

type itemPopularity = {
    id: string,
    images: Array<string>,
    name: string,
    quantity: number
}

const Popular = () => {
    const [itemPopularity, setItemPopularity] = useState<Array<itemPopularity> | null>(null)

    useEffect(() => {
        if (itemPopularity === null) {
            getPopularity(setItemPopularity)
        }
    }
    )



    return <div>
        <MoonLoader
            color={"red"}
            loading={itemPopularity === null}
            size={150}
            aria-label="Loading Spinner"
            data-testid="loader"
        />

        <Transition show={itemPopularity !== null}>
            <div className="transition duration-500 ease-in data-[closed]:opacity-0">
                {
                    (itemPopularity !== null) ? itemPopularity.map((item: itemPopularity, index: number) => (
                        <div className="flex items-center space-x-10">
                            <p key={`${item.id}-rank`}>
                                {index + 1}
                            </p>
                            <div className="flex flex-col">
                                <p>{item.name}</p>
                                <img src={item.images[0]} alt="" className="h-20" />
                            </div>
                        </div>
                    )) : null
                }
            </div>
        </Transition>
    </div >
}

export default Popular