import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { BrandLockup } from '@/components/brand/BrandLockup';
import { SiteFooter } from '@/components/brand/SiteFooter';

export const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background selection:bg-primary/20">
      <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <BrandLockup variant="nav" to="/" />
          <nav className="flex items-center gap-4 sm:gap-6 text-sm font-medium">
            <Link to="/login" className="text-slate-400 transition-colors hover:text-slate-100">
              Log In
            </Link>
            <Link
              to="/register"
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors text-sm font-semibold"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <SiteFooter />
    </div>
  );
};
