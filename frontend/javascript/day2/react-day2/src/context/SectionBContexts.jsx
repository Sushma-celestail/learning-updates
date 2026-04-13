import React, { createContext, useContext, useState, useEffect } from 'react';

// Q4 Contexts
const ThemeContext = createContext();
const LanguageContext = createContext();

export const AppProviders = ({ children }) => {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [lang, setLang] = useState(localStorage.getItem('lang') || 'en');

  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.className = theme;
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('lang', lang);
  }, [lang]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <LanguageContext.Provider value={{ lang, setLang }}>
        {children}
      </LanguageContext.Provider>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
export const useLanguage = () => useContext(LanguageContext);

// Q5 Cart Context
const CartContext = createContext();

const cartReducer = (state, action) => {
  switch (action.type) {
    case 'ADD':
      const existing = state.find(item => item.id === action.payload.id);
      if (existing) {
        return state.map(item => item.id === action.payload.id ? { ...item, qty: item.qty + 1 } : item);
      }
      return [...state, { ...action.payload, qty: 1 }];
    case 'REMOVE':
      return state.filter(item => item.id !== action.payload);
    case 'INC':
      return state.map(item => item.id === action.payload ? { ...item, qty: item.qty + 1 } : item);
    case 'DEC':
      return state.map(item => item.id === action.payload ? { ...item, qty: Math.max(1, item.qty - 1) } : item);
    case 'CLEAR':
      return [];
    default:
      return state;
  }
};

export const CartProvider = ({ children }) => {
  const [cart, dispatch] = React.useReducer(cartReducer, []);
  
  const total = cart.reduce((acc, item) => acc + item.price * item.qty, 0);
  const count = cart.reduce((acc, item) => acc + item.qty, 0);

  return (
    <CartContext.Provider value={{ cart, dispatch, total, count }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);
