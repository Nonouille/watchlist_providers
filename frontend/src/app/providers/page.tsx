"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useResearch } from "../context/ResearchContext";
import Link from "next/link";

export default function Providers() {

    const {username, countryCode, yourProviders, setYourProviders, refresh, setRefresh} = useResearch();
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


    const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.checked) {
          setYourProviders([...yourProviders, e.target.value]);
        } else {
          setYourProviders(yourProviders.filter((p) => p !== e.target.value));
        }
      };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-l mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-4xl p-6">
                <h3 className="text-lg font-bold text-center text-indigo-600 mb-2">Streaming Providers in your region</h3>
                { !loading ? 
                    <div className="grid grid-cols-2 gap-2">
                        {regionProviders.map((provider) => (
                            <div key={provider} className="flex items-center space-x-2 p-2">
                                <input
                                    type="checkbox"
                                    id={`provider-${provider}`}
                                    value={provider}
                                    checked={yourProviders.includes(provider)}
                                    onChange={(e) => { handleCheckboxChange(e) }}
                                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                />
                                <label htmlFor={`provider-${provider}`} className="text-gray-600">{provider}</label>
                            </div>
                        ))}
                    </div>
                    :
                    <div className="col-span-full flex flex-col items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-3"></div>
                        <p className="text-lg text-gray-600">Loading providers...</p>
                    </div>
                }
                <Link href="/results">
                    <button
                        type="submit"
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-4"
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