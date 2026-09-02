import React, { useEffect, useState } from 'react';
import { HardDrive, FileLock2, FileKey, Activity, Settings, LogOut, LineChart, Menu, X } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { authService, type UserProfile } from '@/services/auth.service';
import { BrandLockup } from '@/components/brand/BrandLockup';
import { BRAND } from '@/brand/constants';

function initialsFromEmail(email?: string) {
  if (!email) return 'AC';
  const local = email.split('@')[0] || '';
  const parts = local.split(/[._-]/).filter(Boolean);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return local.slice(0, 2).toUpperCase() || 'AC';
}

export const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: Activity },
    { name: 'Vault', path: '/vault', icon: HardDrive },
    { name: 'Encrypt', path: '/encrypt', icon: FileLock2 },
    { name: 'Decrypt', path: '/decrypt', icon: FileKey },
    { name: 'Analytics', path: '/analytics', icon: LineChart },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  useEffect(() => {
    const load = async () => {
      try {
        const me = await authService.me();
        setProfile(me);
      } catch {
        // Interceptor handles 401 → login
      }
    };
    load();

    const onProfile = () => load();
    window.addEventListener('aryacrypt-profile-updated', onProfile);
    return () => window.removeEventListener('aryacrypt-profile-updated', onProfile);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  const initials = initialsFromEmail(profile?.email);

  const NavLinks = (
    <nav className="flex-1 px-4 py-6 flex flex-col gap-1">
      {navItems.map((item) => {
        const isActive = location.pathname === item.path;
        return (
          <Link
            key={item.name}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
              isActive
                ? 'bg-primary/15 text-sky-300 border border-primary/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium text-sm">{item.name}</span>
          </Link>
        );
      })}
    </nav>
  );

  const BrandFooter = (
    <div className="px-6 py-4 border-t border-white/5 space-y-1">
      <p className="font-mono text-xs text-slate-500">{BRAND.versionLabel}</p>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-background">
      <aside className="w-64 glass-panel border-r border-white/5 hidden md:flex flex-col">
        <div className="p-6">
          <BrandLockup variant="sidebar" to="/dashboard" />
        </div>
        {NavLinks}
        <div className="mt-auto">
          {BrandFooter}
          <div className="p-4 pt-0">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium text-sm">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 bottom-0 w-64 glass-panel border-r border-white/5 flex flex-col bg-background">
            <div className="p-6 flex items-center justify-between">
              <BrandLockup variant="sidebar" to="/dashboard" />
              <button onClick={() => setMobileOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            {NavLinks}
            <div className="mt-auto">
              {BrandFooter}
              <div className="p-4 pt-0">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="font-medium text-sm">Logout</span>
                </button>
              </div>
            </div>
          </aside>
        </div>
      )}

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-16 glass-panel border-b border-white/5 flex items-center px-4 sm:px-8 justify-between z-10 sticky top-0">
          <div className="flex items-center gap-3">
            <button
              className="md:hidden text-slate-300 hover:text-white p-2 rounded-lg hover:bg-white/5"
              onClick={() => setMobileOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg sm:text-xl font-semibold tracking-tight text-slate-100">
              {navItems.find((n) => n.path === location.pathname)?.name || 'Dashboard'}
            </h1>
          </div>
          <Link to="/settings" className="flex items-center gap-3 group">
            {profile?.email && (
              <span className="hidden sm:block text-sm text-slate-400 group-hover:text-slate-200 transition-colors">
                {profile.email}
              </span>
            )}
            <div className="w-9 h-9 rounded-full border border-sky-500/40 bg-sky-500/10 flex items-center justify-center">
              <span className="text-xs font-semibold text-sky-400">{initials}</span>
            </div>
          </Link>
        </header>

        <div className="flex-1 overflow-y-auto p-4 sm:p-8 relative z-0">{children}</div>
      </main>
    </div>
  );
};
