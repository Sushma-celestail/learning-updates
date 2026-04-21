import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppRouter } from './router/AppRouter';
import { Toaster } from 'react-hot-toast';
import './index.css';

// Force dark mode globally
document.documentElement.classList.add('dark');

// Toaster reads the current theme so toasts match the active palette
const ThemedToaster: React.FC = () => {
  return (
    <Toaster
      position="bottom-right"
      gutter={8}
      toastOptions={{
        duration: 4000,
        style: {
          background: '#1A1A24',
          color: '#F1F5F9',
          borderRadius: '12px',
          padding: '12px 16px',
          fontSize: '14px',
          fontWeight: '500',
          boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.6), 0 8px 10px -6px rgb(0 0 0 / 0.4)',
          border: '1px solid rgba(255,255,255,0.08)',
          minWidth: '280px',
          maxWidth: '380px',
        },
        success: {
          style: { borderLeft: `3px solid #34D399` },
          iconTheme: { primary: '#34D399', secondary: '#1A1A24' },
        },
        error: {
          style: { borderLeft: `3px solid #F87171` },
          iconTheme: { primary: '#F87171', secondary: '#1A1A24' },
        },
        loading: {
          style: { borderLeft: `3px solid #A78BFA` },
          iconTheme: { primary: '#A78BFA', secondary: '#1A1A24' },
        },
      }}
    />
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
        <ThemedToaster />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
