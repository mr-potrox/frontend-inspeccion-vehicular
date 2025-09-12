import React from 'react';
import { Header } from '../Header';
import { Footer } from '../Footer';

export interface LayoutProps {
  children: React.ReactNode
  className?: string
}

export const Layout: React.FC<LayoutProps> = ({ children, className  }) => {
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