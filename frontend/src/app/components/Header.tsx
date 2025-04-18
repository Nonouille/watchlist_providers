import Link from 'next/link';
import React from 'react';

export const Header = () => {
    return (
        <header className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex-shrink-0 text-white text-xl font-bold">
                        FilmChecker
                    </div>
                    
                    <nav className="flex space-x-2">
                        <Link 
                            href="/" 
                            className="text-white hover:bg-blue-700 hover:bg-opacity-50 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                        >
                            Home
                        </Link>
                        <Link 
                            href="/about" 
                            className="text-white hover:bg-blue-700 hover:bg-opacity-50 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                        >
                            About
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    );
};