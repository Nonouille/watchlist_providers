"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useResearch } from "../context/ResearchContext";
import Link from "next/link";

export default function Providers() {

    const { username, countryCode, yourProviders, setYourProviders, refresh, setRefresh } = useResearch();
    const [regionProviders, setRegionProviders] = useState<string[]>([])
    const [loading, setLoading] = useState(false);
    const router = useRouter();



    useEffect(() => {
        setLoading(true);
        if (!username || !countryCode) {
            router.push("/")
        }
        else {
            fetch(`http://localhost:5000/your_providers?username=${username}&country_code=${countryCode}`, {
                method: "GET",
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((data) => {
                    setYourProviders(data.providers);

                    fetch(`http://localhost:5000/get_region_providers?country_code=${countryCode}`, {
                        method: "GET",
                    })
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then((data) => {
                            setRegionProviders(data.providers);
                            setLoading(false);
                        })
                        .catch((error) => console.error("Error fetching region providers:", error));
                })
                .catch((error) => console.error("Error fetching your providers:", error));
        }
    }, [countryCode, setYourProviders, username, router]);
    
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-l mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-4xl p-6">
                <h3 className="text-lg font-bold text-center text-indigo-600 mb-4">Streaming Providers in your region</h3>
                {!loading ?
                    <div className="space-y-4">
                        <div className="relative">
                            <div className="flex items-center border border-gray-300 rounded-md focus-within:ring-indigo-500 focus-within:border-indigo-500">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400 ml-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                                </svg>
                                <select
                                    className="w-full p-2 bg-white appearance-none focus:outline-none text-gray-700"
                                    onChange={(e) => {
                                        if (e.target.value !== "") {
                                            const provider = e.target.value;
                                            if (!yourProviders.includes(provider)) {
                                                setYourProviders([...yourProviders, provider]);
                                            }
                                        }
                                    }}
                                    defaultValue=""
                                >
                                    <option value="" disabled>Add your providers...</option>
                                    {regionProviders
                                        .filter(provider => !yourProviders.includes(provider))
                                        .map((provider) => (
                                            <option key={provider} value={provider}>
                                                {provider}
                                            </option>
                                        ))}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                        </div>
                        <h3 className="text-mg font-bold text-indigo-600 mb-1 mt-6">Your Selected Providers :</h3>
                        <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto">
                            {yourProviders.map((provider) => (
                                <div key={provider} onClick={(e) => {
                                    e.preventDefault();
                                    setYourProviders(yourProviders.filter(p => p !== provider));
                                }} className="flex items-center space-x-2 p-2 hover:bg-gray-50 rounded-md">
                                    <label htmlFor={`provider-${provider}`} className="text-gray-600 cursor-pointer flex-1 hover:text-red-400">{provider}</label>
                                </div>
                            ))}
                        </div>
                    </div>
                    :
                    <div className="col-span-full flex flex-col items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-3"></div>
                        <p className="text-lg text-gray-600">Loading providers...</p>
                    </div>
                }
                <Link href="/results">
                    <button
                        type="button"
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-4 cursor-pointer"
                    >
                        Get your watchlist streaming providers
                    </button>
                </Link>
                <div className="mt-2 ml-0.5 flex items-center space-x-1 pl-4 pt-2">
                    <input type="checkbox" id="refresh" checked={refresh} onChange={() => setRefresh(!refresh)} className='h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded' />
                    <label htmlFor="refresh" className=" text-sm text-gray-700">Search letterboxd again</label>
                </div>
            </div>
        </div>
    )
}