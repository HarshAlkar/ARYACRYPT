import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LandingPage } from './app/LandingPage';
import { Login } from './app/Login';
import { Register } from './app/Register';
import { Dashboard } from './pages/Dashboard';
import { Decrypt } from './pages/Decrypt';
import { Vault } from './pages/Vault';
import { Encrypt } from './pages/Encrypt';
import { Settings } from './pages/Settings';
import { Analytics } from './pages/Analytics';
import { MainLayout } from './layouts/MainLayout';
import { authService } from './services/auth.service';
import { getAccessToken } from './services/tokenStore';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const [ready, setReady] = useState(false);
  const [ok, setOk] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (getAccessToken()) {
          if (!cancelled) {
            setOk(true);
            setReady(true);
          }
          return;
        }
        const restored = await authService.bootstrapSession();
        if (!cancelled) {
          setOk(restored);
          setReady(true);
        }
      } catch {
        if (!cancelled) {
          setOk(false);
          setReady(true);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-slate-500 font-sans">
        Restoring session…
      </div>
    );
  }
  if (!ok) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<LandingPage />} />
        </Route>

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/decrypt" element={<ProtectedRoute><Decrypt /></ProtectedRoute>} />
        <Route path="/vault" element={<ProtectedRoute><Vault /></ProtectedRoute>} />
        <Route path="/encrypt" element={<ProtectedRoute><Encrypt /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
