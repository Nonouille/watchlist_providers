"use client";
import React, { useEffect, useState } from 'react';
import { useResearch } from '@/app/context/ResearchContext';
import { API_BASE_URL } from '@/app/config/config';
import { useRouter } from 'next/navigation';

export default function Home() {

  const { username, setUsername, username2, setUsername2, setDualMode, countryCode, setCountryCode } = useResearch();
  const [regions, setRegions] = useState<string[]>([]);
  const [showSecondUser, setShowSecondUser] = useState<boolean>(!!username2);
  const router = useRouter();

  useEffect(() => {
    fetch(`${API_BASE_URL}/regions`, {
      method: "GET",
    })
      .then((response) => response.json())
      .then((data) => {
        setRegions(data.regions);
      })
      .catch((error) => console.error("Error:", error));
  }, []);

  return (
    <main className="flex flex-col min-h-screen w-full bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-gray-900 dark:to-indigo-950 py-8 px-4">
      <div className="max-w-md mx-auto w-full bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden p-5">
      <h3 className="text-xl font-bold text-center text-indigo-600 dark:text-indigo-300 mb-4">Enter your Letterboxd username and country code</h3>
      <form className="space-y-5">
        <div className="space-y-2">
        <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {showSecondUser ? "Username 1:" : "Username:"}
        </label>
        <input
          type="text"
          id="username"
          name="username"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder='Enter your Letterboxd username'
          className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-500"
        />
        </div>
        {showSecondUser && (
          <div className="space-y-2">
            <label htmlFor="username2" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Username 2:
            </label>
            <input
              type="text"
              id="username2"
              name="username2"
              value={username2}
              onChange={(e) => setUsername2(e.target.value)}
              placeholder='Enter a second Letterboxd username'
              className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-500"
            />
          </div>
        )}

        <div className="space-y-2">
        <label htmlFor="country_code" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Country Code:</label>
        <select
          id="country_code"
          name="country_code"
          required
          value={countryCode}
          onChange={(e) => setCountryCode(e.target.value)}
          className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 dark:text-gray-100"
        >
          <option value="">Select a country code</option>
          {regions.map((region) => (
          <option key={region} value={region}>{region}</option>
          ))}
        </select>
        </div>

        <div className="pt-2">
          <button
            type="button"
            onClick={() => {
              setDualMode(Boolean(username2));
              router.push("/providers");
            }}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-offset-gray-800"
          >
            Next
          </button>
        </div>
        {!showSecondUser ? (
          <div className="pt-1">
            <button
              type="button"
              onClick={() => setShowSecondUser(true)}
              className="w-full flex justify-center py-2 px-4 border border-indigo-200 dark:border-indigo-700 rounded-md shadow-sm text-sm font-medium text-indigo-700 dark:text-indigo-200 bg-white dark:bg-gray-800 hover:bg-indigo-50 dark:hover:bg-gray-700 focus:outline-none"
            >
              Add a second username
            </button>
          </div>
        ) : (
          <div className="pt-1">
            <button
              type="button"
              onClick={() => {
                setUsername2("");
                setShowSecondUser(false);
              }}
              className="w-full flex justify-center py-2 px-4 border border-red-200 dark:border-red-700 rounded-md shadow-sm text-sm font-medium text-red-700 dark:text-red-200 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-gray-700 focus:outline-none"
            >
              Remove second username
            </button>
          </div>
        )}
      </form>
      </div>
    </main>
  );
}
