import { createContext, useState, useMemo } from "react";
export const ThemeContext =createContext();

export function ThemeProvider({children}){
    const [theme,setTheme]=useState("light");

    const toggleTheme =() => {
        setTheme(prev => (prev === "light" ? "dark": "light"));

    };
    //optimise to avoide unnecessary re- render
    const value =useMemo (()=>({
        theme,
        toggleTheme
    }),[theme]);
    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
}