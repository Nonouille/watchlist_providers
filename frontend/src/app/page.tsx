"use client";
import React, { useEffect, useState } from 'react';
import { useResearch } from '@/app/context/ResearchContext';
import Link from 'next/link';

export default function Home() {

  const { username, setUsername, countryCode, setCountryCode } = useResearch();
  const [regions, setRegions] = useState<string[]>([]);

  useEffect(() => {
    fetch("http://localhost:5000/regions", {
      method: "GET",
    })
      .then((response) => response.json())
      .then((data) => {
        setRegions(data.regions);
      })
      .catch((error) => console.error("Error:", error));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-4xl p-6">
        <h3 className="text-xl font-bold text-center text-indigo-600 mb-2">Enter your Letterboxd username and country code</h3>
        <form className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username:</label>
            <input
              type="text"
              id="username"
              name="username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder='Enter your Letterboxd username'
              className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 placeholder-gray-300"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="country_code" className="block text-sm font-medium text-gray-700">Country Code:</label>
            <select
              id="country_code"
              name="country_code"
              required
              value={countryCode}
              onChange={(e) => setCountryCode(e.target.value)}
              className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
            >
              <option value="">Select a country code</option>
              {regions.map((region) => (
                <option key={region} value={region}>{region}</option>
              ))}
            </select>
          </div>

          <div className="pt-4">
            <Link href="/providers">
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Get your region&apos;s streaming providers
              </button>
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
