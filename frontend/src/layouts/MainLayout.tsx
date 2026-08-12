import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';

export const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background selection:bg-primary/20">
      <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2 group">
            <ShieldAlert className="h-6 w-6 text-primary group-hover:scale-110 transition-transform" />
            <span className="font-bold text-xl tracking-tight">AryaCrypt</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link to="/login" className="text-gray-300 transition-colors hover:text-primary">Log In</Link>
            <Link to="/register" className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors shadow-[0_0_15px_rgba(34,197,94,0.3)]">Get Started</Link>
          </nav>
        </div>
      </header>
      
      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-border/50 py-6">
        <div className="container mx-auto px-4 flex flex-col items-center justify-between gap-4 md:flex-row">
          <p className="text-sm leading-loose text-gray-500">
            Built for security. Inspired by history.
          </p>
          <p className="text-sm text-gray-500">
            © 2026 AryaCrypt. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};
