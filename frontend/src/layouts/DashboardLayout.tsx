import React from 'react';
import { Shield, HardDrive, FileLock2, FileKey, Activity, Settings, LogOut, LineChart } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: Activity },
    { name: 'My Vault', path: '/vault', icon: HardDrive },
    { name: 'Encrypt File', path: '/encrypt', icon: FileLock2 },
    { name: 'Decrypt File', path: '/decrypt', icon: FileKey },
    { name: 'Analytics', path: '/analytics', icon: LineChart },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex bg-background">
      {/* Sidebar */}
      <aside className="w-64 glass-panel border-r border-white/5 hidden md:flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <Shield className="w-8 h-8 text-sky-400 text-glow" />
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-sky-400 to-purple-500">
            AryaCrypt
          </span>
        </div>
        
        <nav className="flex-1 px-4 py-8 flex flex-col gap-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 ${
                  isActive 
                    ? 'bg-primary/20 text-sky-300 border border-primary/30 neon-glow' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>
        
        <div className="p-4 mt-auto">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Secure Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-20 glass-panel border-b border-white/5 flex items-center px-8 justify-between z-10 sticky top-0">
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">
            {navItems.find(n => n.path === location.pathname)?.name || "Dashboard"}
          </h1>
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-sky-500 to-purple-600 p-[2px] cursor-pointer shadow-[0_0_10px_rgba(168,85,247,0.3)]">
              <div className="w-full h-full bg-background rounded-full flex items-center justify-center">
                <span className="text-sm font-bold text-sky-400">AC</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-8 relative z-0">
          {children}
        </div>
      </main>
    </div>
  );
};
