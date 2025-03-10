'use client';
import React, { useEffect, useState } from 'react';

export default function Home() {
  const [username, setUsername] = useState("");
  const [countryCode, setCountryCode] = useState("");
  const [regions, setRegions] = useState<string[]>([]);
  const [yourProviders, setYourProviders] = useState<string[]>([]);
  const [regionProviders, setRegionProviders] = useState<string[]>([]);
  const [refresh, setRefresh] = useState(false);

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

  const findProviders = (e: React.FormEvent) => {
    e.preventDefault();

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

        fetch(`http://localhost:5000/region_providers?country_code=${countryCode}`, {
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
          })
          .catch((error) => console.error("Error fetching region providers:", error));
        })
      .catch((error) => console.error("Error fetching your providers:", error));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setYourProviders([...yourProviders, e.target.value]);
    } else {
      setYourProviders(yourProviders.filter((p) => p !== e.target.value));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl p-6">
        <h1 className="text-3xl font-bold text-center text-indigo-600 mb-2">Letterboxd Watchlist Streaming Provider</h1>
        <h3 className="text-lg text-gray-600 text-center mb-8">Enter your Letterboxd username and country code</h3>
        
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
            <button
              type="submit"
              onClick={findProviders}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Get your region&apos;s streaming providers
            </button>
          </div>

          {regionProviders.length > 0 && (
            <div className="mt-8">
              <h2 className="text-lg font-bold text-center text-indigo-600 mb-2">Streaming Providers in your region</h2>
                <div className="grid grid-cols-2 gap-2">
                {regionProviders.map((provider) => (
                  <div key={provider} className="flex items-center space-x-2 p-2">
                  <input 
                    type="checkbox" 
                    id={`provider-${provider}`}
                    value={provider} 
                    checked={yourProviders.includes(provider)}
                    onChange={(e) => {handleCheckboxChange(e)}}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor={`provider-${provider}`} className="text-gray-600">{provider}</label>
                  </div>
                ))}
                </div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-4"
              >
                Get your watchlist streaming providers
              </button>
              <div className="mt-2 ml-0.5 flex items-center space-x-1">
                <input type="checkbox" id="refresh" checked={refresh} onChange={() => setRefresh(!refresh)} className='h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded' />
                <label htmlFor="refresh" className=" text-sm text-gray-700">Search letterboxd again</label>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
