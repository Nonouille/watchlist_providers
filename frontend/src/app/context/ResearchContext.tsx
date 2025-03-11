"use client";
import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define the shape of our context state
interface ResearchContextType {
    username: string;
    setUsername: (username: string) => void;
    countryCode: string;
    setCountryCode: (countryCode: string) => void;
    yourProviders: string[];
    setYourProviders: (provider: string[]) => void;
    refresh: boolean;
    setRefresh: (refresh: boolean) => void;
}

// Create the context with an initial default value
const ResearchContext = createContext<ResearchContextType | undefined>(undefined);

// Props for our provider component
interface ResearchProviderProps {
    children: ReactNode;
}

// Provider component that will wrap parts of our app that need access to the context
export const ResearchProvider: React.FC<ResearchProviderProps> = ({ children }) => {
    const [username, setUsername] = useState<string>('');
    const [countryCode, setCountryCode] = useState<string>('');
    const [yourProviders, setYourProviders] = useState<string[]>([]);
    const [refresh, setRefresh] = useState<boolean>(false);

    const value = {
        username,
        setUsername,
        countryCode,
        setCountryCode,
        yourProviders,
        setYourProviders,
        refresh,
        setRefresh,
    };

    return (
        <ResearchContext.Provider value={value}>
            {children}
        </ResearchContext.Provider>
    );
};

// Custom hook to use the research context
export const useResearch = (): ResearchContextType => {
    const context = useContext(ResearchContext);
    
    if (context === undefined) {
        throw new Error('useResearch must be used within a ResearchProvider');
    }
    
    return context;
};