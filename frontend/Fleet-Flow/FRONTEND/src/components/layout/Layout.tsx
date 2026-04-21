import React from 'react';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />

      {/* Main content — offset for desktop sidebar */}
      <div className="lg:pl-60">
        <Navbar />

        {/* Page content — offset for fixed navbar */}
        <main className="pt-16">
          <div className="p-6 lg:p-8 animate-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
