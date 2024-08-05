import { useContext, useEffect, useState } from "react";
import { endpointURL } from "../lib/shared"
import MoonLoader from "react-spinners/MoonLoader";
import { Transition } from "@headlessui/react";
import { AppContext } from '../contexts';

type Product = {
    default_price: string,
    livemode: true,
    metadata: {},
    object: string,
    package_dimensions: {},
    created: string,
    statement_descriptor: string,
    attributes: [
        string
    ],
    shippable: true,
    url: string,
    name: string,
    active: true,
    updated: string,
    images: [
        string
    ],
    marketing_features: [
        {}
    ],
    tax_code: string,
    description: string,
    id: string,
    unit_label: string,
    type: string
}

type Price = {
    id: string,
    object: string,
    active: true,
    billing_scheme: string,
    created: number,
    currency: string,
    custom_unit_amount: {},
    livemode: true,
    lookup_key: string,
    metadata: {},
    nickname: string,
    product: string,
    recurring: {},
    tax_behavior: string,
    tiers_mode: string,
    transform_quantity: {},
    type: string,
    unit_amount: number,
    unit_amount_decimal: string
}

const getProducts = async (): Promise<Array<Product> | null> => {
    try {
        const response = await fetch(
            `${endpointURL}/stripe/products`, { method: "GET", }
        )
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const data = await response.json()
        return data
    }
    catch (e) {
        console.log((e as Error).message)
        return null

    }
}


const getPrices = async (): Promise<Array<Price> | null> => {
    try {
        const response = await fetch(
            `${endpointURL}/stripe/prices`, { method: "GET" }
        )
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const data = await response.json()
        return data
    }
    catch (e) {
        console.log((e as Error).message)
        return null

    }
}


const Products = () => {
    const [products, setProducts] = useState<Array<Product> | null>(null)
    const [prices, setPrices] = useState<Array<Price> | null>(null)
    const [loading, setLoading] = useState(true)
    const appContext = useContext(AppContext)


    useEffect(() => {
        const setFetchedProducts = async () => {
            if (products === null) {
                const fetchedProducts = await getProducts()
                setProducts(fetchedProducts)
            }
        }

        const setFetchedPrices = async () => {
            if (prices === null) {
                const fetchedPrices = await getPrices()
                setPrices(fetchedPrices)
            }
        }

        setFetchedProducts()
        setFetchedPrices()

        if (products !== null && prices !== null) {
            setLoading(false)
        }
    }, [prices, products])

    const getProductPrice = (default_price: string): string | null => {
        if (prices !== null) {
            for (let i = 0; i < prices.length; i++) {
                if (default_price === prices[i].id) {
                    return (prices[i].unit_amount / 100).toFixed(2)
                }
            }
        }
        return null
    }

    const productCounter = (product: Product): number => {
        const cart: {
            [product_id: string]: { [quantity: string]: number }
        } = appContext.cart
        if (product.id in cart) {
            return cart[product.id]["quantity"]
        }
        return 0

    }

    const decrementCart = (product: Product): void => {
        const cart = { ...appContext.cart }
        if (product.id in cart) {
            const quantity = cart[product.id]["quantity"]
            if (quantity > 0) {
                cart[product.id]["quantity"] -= 1
                appContext.setCart(cart)
            }
            else {
                delete cart[product.id]
                appContext.setCart(cart)
            }
        }
    }
    const incrementCart = (product: Product): void => {
        const cart = { ...appContext.cart }
        if (!(product.id in cart)) {
            cart[product.id] = { "name": product.name, "images": product.images, "quantity": 1, "price": product.default_price }
            appContext.setCart(cart)
        } else {
            cart[product.id]["quantity"] += 1
            appContext.setCart(cart)
        }
    }


    return <>
        <MoonLoader
            color={"red"}
            loading={loading}
            size={150}
            aria-label="Loading Spinner"
            data-testid="loader"
        />

        <Transition show={!loading}>
            <div className="flex space-x-4 transition duration-500 ease-in data-[closed]:opacity-0">
                {
                    (prices !== null && products !== null) ? products.map((product: Product) => (
                        <div className="flex flex-col h-[200px] w-[200px] items-center border rounded-lg p-5 space-y-4" key={product.id + '-div'}>
                            <p key={product.id + '-name'}>{product.name}</p>
                            <div className="border h-[50px] w-[50px]">
                                <img
                                    key={product.id + '-image'}
                                    src={product.images[0]}
                                    alt={product.description}
                                    className="object-fill h-min-[50px]"
                                />
                            </div>
                            <div key={product.id + '-price-div'}>
                                price: {getProductPrice(product.default_price)}
                            </div>
                            <div key={product.id + '-counter-div'} className="flex justify-end space-x-5">
                                <button key={product.id + '-decrement-button'} type="button" onClick={() => decrementCart(product)}><p>-</p></button>
                                <p key={product.id + '-counter'}> {productCounter(product)}</p>
                                <button key={product.id + '-increment-div'} type="button" onClick={() => incrementCart(product)}><p>+</p></button>
                            </div>
                        </div>
                    )) : null
                }
            </div>
        </Transition>
    </>

}

export default Products