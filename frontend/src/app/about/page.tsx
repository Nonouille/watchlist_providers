import React from 'react';

export default function About() {
    return (
        <div className="w-full h-full mx-auto px-4 py-8 bg-gray-50">
            <h1 className="text-3xl font-bold mb-6 text-gray-800 text-center">About Film Checker</h1>
            
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
                <p className="mb-4 text-gray-700">
                    Film Checker is a platform designed to help you discover and keep track of movies.
                </p>
                
                <p className="mb-4 text-gray-700">
                    This website was created with passion by <span className="font-semibold text-indigo-600">Nonouille</span>.
                </p>
                
                <p className="text-gray-700">
                    Thank you for visiting Film Checker. We hope you enjoy using our service to enhance your film watching experience!
                </p>
            </div>
        </div>
    );
}