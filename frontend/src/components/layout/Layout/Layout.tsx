import React from 'react';
import { Header } from '../Header';
import { Footer } from '../Footer';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <Header />
        {children}
        <Footer />
      </div>
    </div>
  );
};