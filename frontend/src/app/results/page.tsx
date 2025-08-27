"use client";
import React, { useEffect, useState } from 'react';
import Link from "next/link";
import { ResultCard } from '@/app/components/ResultCard';
import { useResearch } from '@/app/context/ResearchContext';
import { useRouter } from 'next/navigation';
import { Film } from '../types/Film';
import { API_BASE_URL } from '@/app/config/config';

export default function Result() {
    const { username, countryCode, yourProviders, refresh } = useResearch();
    const [results, setResults] = useState<Film[]>([]);
    const [sortedResults, setSortedResults] = useState<Film[]>([]);
    const [genres, setGenres] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>("");
    const routeur = useRouter();

    useEffect(() => {
        setLoading(true);
        if (!username || !countryCode) {
            routeur.push("/");
            return;
        }

        fetch(`${API_BASE_URL}/genres`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    setError(`HTTP error! Status: ${response.status}`);
                    setLoading(false);
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                if (data && Array.isArray(data.genres)) {
                    setGenres(data.genres);
                } else {
                    console.error("Invalid genres data:", data);
                    setError("Invalid genres data received.");
                    setLoading(false);
                }
            })
            .catch((error) => {
                console.error("Error fetching genres:", error);
                setError("Failed to load genres. Please try again.");
            });

        fetch(`${API_BASE_URL}/results`, {
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
                    setError(`HTTP error! Status: ${response.status}`);
                    setLoading(false);
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                if (Array.isArray(data)) {
                    const sortedData = [...data].sort((a: Film, b: Film) => b.note - a.note);
                    setResults(sortedData);
                    setSortedResults(sortedData); // Set sortedResults with the same data
                    setLoading(false);
                } else {
                    setError("Invalid results data received");
                    console.error("Invalid results data:", data);
                    setLoading(false);
                }
            })
            .catch((error) => {
                console.error("Error fetching watchlist providers:", error);
                setError("Failed to load results. Please try again.");
                setLoading(false);
            });
    }, [countryCode, refresh, username, yourProviders, routeur]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-gray-900 dark:to-indigo-950 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden md:max-w-4xl p-6">
                <h3 className="text-3xl font-bold text-center text-indigo-600 dark:text-indigo-400 mb-10">Your Watchlist Results</h3>
                {!loading ?
                    <div className="">
                        {!error ? (
                            <>
                                {results && results.length > 0 ? (
                                    <>
                                        <div className="mb-6 flex justify-center">
                                            <label htmlFor="sort" className="mr-3 text-lg font-medium text-gray-700 dark:text-gray-200">
                                                Genres:
                                            </label>
                                            <select
                                                id="sort"
                                                className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-200 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 p-2"
                                                onChange={(e) => {
                                                    const selectedGenre = e.target.value;
                                                    if (selectedGenre === "all") {
                                                        setSortedResults(results);
                                                    } else {
                                                        const filteredResults = results.filter((film) => film.genres.includes(selectedGenre));
                                                        setSortedResults(filteredResults);
                                                    }
                                                }}
                                                defaultValue="all"
                                            >
                                                <option value="all">All Genres</option>
                                                {genres.map((genre) => (
                                                    <option key={genre} value={genre}>
                                                        {genre.charAt(0).toUpperCase() + genre.slice(1)}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                        <ResultCard films={sortedResults} />
                                    </>
                                ) : (
                                    <div className="col-span-full text-center py-12">
                                        <p className="text-lg text-gray-600 dark:text-gray-300">No results found. Try different filters or providers.</p>
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="col-span-full text-center py-12">
                                <p className="text-lg text-red-600 dark:text-red-400">{error}</p>
                            </div>
                        )}
                    </div>
                    :
                    <>
                        <div className="col-span-full flex flex-col items-center justify-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-3"></div>
                            <p className="text-lg text-gray-600 dark:text-gray-300">Loading providers...</p>
                            <p className="text-sm text-gray-400 dark:text-gray-500">This can take up to 2 minutes</p>
                        </div>
                    </>
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