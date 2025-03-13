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
            fetch(`https://cine.pyarnaud.studio/api/your_providers?username=${username}&country_code=${countryCode}`, {
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

                    fetch(`https://cine.pyarnaud.studio/api/get_region_providers?country_code=${countryCode}`, {
                        method: "GET",
                    })
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then((data) => {
                            setRegionProviders(data.providers.sort((a : string, b : string) => a.localeCompare(b)));
                            setLoading(false);
                        })
                        .catch((error) => console.error("Error fetching region providers:", error));
                })
                .catch((error) => console.error("Error fetching your providers:", error));
        }
    }, [countryCode, setYourProviders, username, router]);
    
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 to-indigo-900 dark:from-gray-900 dark:to-black py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-l mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden md:max-w-4xl p-6">
                <h3 className="text-lg font-bold text-center text-indigo-600 dark:text-indigo-300 mb-4">Streaming Providers in your region</h3>
                {!loading ?
                    <div className="space-y-4">
                        <div className="relative">
                        <h3 className="text-mg font-bold text-indigo-600 dark:text-indigo-300 mb-3 mt-5">Add your providers :</h3>
                            <div className="flex items-center border border-gray-300 dark:border-gray-600 rounded-md focus-within:ring-indigo-500 focus-within:border-indigo-500">
                                <select
                                    className="w-full p-2 bg-white dark:bg-gray-700 appearance-none focus:outline-none text-gray-700 dark:text-gray-200"
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
                                    <option value="">Select a providers...</option>
                                    {regionProviders
                                        .filter(provider => !yourProviders.includes(provider))
                                        .map((provider) => (
                                            <option key={provider} value={provider}>
                                                {provider}
                                            </option>
                                        ))}
                                </select>
                                <div className="pointer-events-none absolute right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                        </div>
                        <hr className="my-5 h-0.25 border-t-0 bg-gray-200 dark:bg-gray-700" />
                        <h3 className="text-mg font-bold text-indigo-600 dark:text-indigo-300 mb-3 mt-0">Your selected providers :</h3>
                        <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto mb-0">
                            {yourProviders.map((provider) => (
                                <div key={provider} onClick={(e) => {
                                    e.preventDefault();
                                    setYourProviders(yourProviders.filter(p => p !== provider));
                                }} className="flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md">
                                    <label htmlFor={`provider-${provider}`} className="text-gray-600 dark:text-gray-300 cursor-pointer flex-1 hover:text-red-400">{provider}</label>
                                </div>
                            ))}
                        </div>

                        <div className="mt-0">
                            <div className="flex justify-end mr-20 ">
                                <button
                                    type="button"
                                    onClick={() => setYourProviders([])}
                                    className="py-1.5 px-3 border border-red-300 dark:border-red-500 rounded-md shadow-md text-sm text-red-600 dark:text-red-400 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-1 focus:ring-offset-1 focus:ring-red-500"
                                >
                                    Clear All Selected Providers
                                </button>
                            </div>
                        </div>
                    </div>
                    :
                    <div className="col-span-full flex flex-col items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-3"></div>
                        <p className="text-lg text-gray-600 dark:text-gray-300">Loading providers...</p>
                    </div>
                }
                <hr className="my-5 h-0.25 border-t-0 bg-gray-200 dark:bg-gray-700" />     
                <Link href="/results" className="flex justify-center">
                    <button
                        type="button"
                        className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-4 cursor-pointer"
                    >
                        Get your watchlist streaming providers
                    </button>
                </Link>
                <div className="mt-2 ml-0.5 flex items-center space-x-1 pl-4 pt-2">
                    <input type="checkbox" id="refresh" checked={refresh} onChange={() => setRefresh(!refresh)} className='h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded' />
                    <label htmlFor="refresh" className="text-sm text-gray-700 dark:text-gray-300">Search letterboxd again</label>
                </div>
            </div>
        </div>
    )
}