import { AppContext } from "../contexts"
import { useContext, useEffect, useState } from "react"
import { endpointURL } from "../lib/shared"

type PastPurchase = {
    quantity: number,
    created: number,
    currency: string,
    product: number,
    unit_amount: number,
    details: {
        images: Array<string>,
        name: string
    },
}

const getPastPurchases = async (setPastPurchase: (purchases: PastPurchase[]) => void) => {
    try {
        const response = await fetch(
            `${endpointURL}/stripe/current-user-past-purchases`, {
            method: "GET",
            credentials: "include"
        }
        )
        if (!response.ok) {
            throw Error(`Response Status: ${response.status}`)
        }
        const data = await response.json()
        setPastPurchase(data)

    } catch (e) {
        throw (e as Error).message
    }

}




const Recent = () => {
    const [pastPurchases, setPastPurchases] = useState<Array<PastPurchase>>(new Array<PastPurchase>())
    const context = useContext(AppContext);
    useEffect(() => {

        if (context.authorized && pastPurchases.length === 0) {
            getPastPurchases(setPastPurchases)
        }
    }
    )
    return <>
        {
            (context.authorized) ?
                <div className="flex flex-col space-y-5">
                    {
                        pastPurchases.map((item: PastPurchase, index: number) => (
                            <div className="flex space-x-5 align-middle items-center" key={`${item.product}-${item.created}-${index}`}>
                                <p>created on: {Date(item.created * 1000).toString()}</p>
                                <div className="flex flex-col">
                                    <p>{item.details.name}</p>
                                    <img src={item.details.images[0]} alt="" className="h-10" />
                                </div>
                                <p>quantity: {item.quantity}</p>
                                <p>price: {item.unit_amount / 100} {item.currency}</p>
                                <p>spend: {item.unit_amount / 100 * item.quantity} {item.currency}</p>
                            </div>
                        ))
                    }
                </div>
                : <p>login to view past purchases </p>
        }
    </>

}

export default Recent