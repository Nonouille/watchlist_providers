"use client";
import React, { useEffect, useState } from 'react';
import Link from "next/link";
import { ResultCard } from '@/app/components/ResultCard';
import { useResearch } from '@/app/context/ResearchContext';
import { useRouter } from 'next/navigation';
import { Film } from '../types/Film';

export default function Result() {
    const { username, countryCode, yourProviders, refresh } = useResearch();
    const [results, setResults] = useState<Film[]>([]);
    const [loading, setLoading] = useState(false);
    const routeur = useRouter();

    useEffect(() => {
        setLoading(true);
        if (!username || !countryCode) {
            routeur.push("/");
        }
        else {
            fetch(`https://cine.pyarnaud.studio/api/results`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username: username,
                    country_code: countryCode,
                    providers: yourProviders,
                    refresh: refresh,
                }),
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((data) => {
                    data.sort((a: Film, b: Film) => b.note - a.note);
                    setResults(data);
                    setLoading(false);
                })
                .catch((error) => console.error("Error fetching watchlist providers:", error));
            }
    }, [countryCode, refresh, username, yourProviders, routeur]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-gray-900 dark:to-indigo-950 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden md:max-w-4xl p-6">
            <h3 className="text-3xl font-bold text-center text-indigo-600 dark:text-indigo-400 mb-10">Your Watchlist Results</h3>
            {!loading ? 
                <div className="">
                {results && results.length > 0 ? (
                    <ResultCard films={results} />
                ) : (
                    <div className="col-span-full text-center py-12">
                    <p className="text-lg text-gray-600 dark:text-gray-300">No results found. Try different filters or providers.</p>
                    </div>
                )}
                </div>
            : 
                <div className="col-span-full flex flex-col items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-3"></div>
                <p className="text-lg text-gray-600 dark:text-gray-300">Loading providers...</p>
                </div>
            }
            <div className="mt-8 text-center">
                <Link href="/">
                <button
                    className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white dark:bg-indigo-700 dark:hover:bg-indigo-600 rounded-md shadow-sm"
                >
                    Back to Search
                </button>
                </Link>
            </div>
            </div>
        </div>
    );
}