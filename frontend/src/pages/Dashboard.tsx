import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { HardDrive, ShieldAlert, FileKey2, Activity, Lock, Unlock, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { StatBox } from '../components/ui/StatBox';
import { Card } from '@/components/ui/card';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { fileService, type VaultStats } from '../services/file.service';
import { loadPrefs } from '../services/auth.service';

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1, transition: { type: "spring" as const, stiffness: 300 } }
};

function formatTrend(pct: number): string | undefined {
  if (pct === 0) return '0%';
  return `${pct > 0 ? '+' : ''}${pct}%`;
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<VaultStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const prefs = loadPrefs();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await fileService.getStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch vault stats:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  const capacityGB = stats ? stats.storage_capacity_bytes / (1024 ** 3) : 5;
  const storageUsedGB = stats ? (stats.storage_used_bytes / (1024 ** 3)).toFixed(2) : '0.00';
  const storagePercentage = stats
    ? Math.min(100, Math.round((stats.storage_used_bytes / Math.max(stats.storage_capacity_bytes, 1)) * 100))
    : 0;

  const statCards = [
    {
      title: "Total Files Secured",
      value: (stats?.total_files ?? 0).toString(),
      icon: FileKey2,
      color: "cyan" as const,
      trend: stats ? formatTrend(stats.trends.files) : undefined,
    },
    {
      title: "Total Encrypted",
      value: (stats?.total_encrypted ?? 0).toString(),
      icon: Lock,
      color: "purple" as const,
      trend: stats ? formatTrend(stats.trends.encrypt) : undefined,
    },
    {
      title: "Total Decrypted",
      value: (stats?.total_decrypted ?? 0).toString(),
      icon: Unlock,
      color: "green" as const,
      trend: stats ? formatTrend(stats.trends.decrypt) : undefined,
    },
    {
      title: "Security Alerts",
      value: (stats?.security_alerts ?? 0).toString(),
      icon: ShieldAlert,
      color: "red" as const,
    },
  ];

  const recentActivity = (stats?.recent_activity ?? []).slice(0, prefs.compactActivity ? 8 : 5);
  const rowPad = prefs.compactActivity ? 'py-2.5' : 'py-4';

  return (
    <DashboardLayout>
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="max-w-7xl mx-auto flex flex-col gap-8"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, i) => (
            <motion.div key={i} variants={itemVariants}>
              <StatBox {...stat} />
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <Card hoverEffect className="h-full flex flex-col p-6">
              <div className="flex items-center gap-3 mb-6">
                <HardDrive className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-slate-100">Vault Storage</h2>
              </div>
              
              <div className="flex-1 flex flex-col justify-center gap-8 py-6">
                <div className="relative flex justify-center items-center">
                  <div className="absolute w-40 h-40 rounded-full border-4 border-white/5"></div>
                  <div className="absolute w-40 h-40 rounded-full border-4 border-purple-500/20 border-t-purple-500 animate-[spin_3s_linear_infinite]"></div>
                  <div className="flex flex-col items-center justify-center relative z-10">
                    <span className="text-3xl font-bold text-glow">{storagePercentage}<span className="text-xl text-slate-400">%</span></span>
                    <span className="text-sm text-slate-400 mt-1">Used</span>
                  </div>
                </div>
                
                <div className="space-y-4 px-2">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-400">Encrypted Data</span>
                      <span className="font-medium text-slate-200">{storageUsedGB} GB</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${storagePercentage}%` }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        className="h-full bg-gradient-to-r from-sky-400 to-purple-500"
                      />
                    </div>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Vault Capacity</span>
                    <span className="font-medium text-slate-400">{capacityGB.toFixed(1)} GB</span>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants} className="lg:col-span-2">
            <Card hoverEffect className="h-full p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-sky-400" />
                  <h2 className="text-lg font-semibold text-slate-100">Recent Activity</h2>
                </div>
                <Link
                  to="/analytics"
                  className="text-sm font-medium text-sky-400 hover:text-sky-300 transition-colors"
                >
                  View Analytics
                </Link>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-white/10 text-slate-400 text-sm">
                      <th className="pb-3 font-medium">Action</th>
                      <th className="pb-3 font-medium">File Name</th>
                      <th className="pb-3 font-medium">Time</th>
                      <th className="pb-3 font-medium text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-slate-500">
                          <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                          Loading activity...
                        </td>
                      </tr>
                    ) : recentActivity.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-slate-500">
                          No recent activity found in your vault.
                        </td>
                      </tr>
                    ) : recentActivity.map((log) => (
                      <motion.tr 
                        whileHover={{ backgroundColor: 'rgba(255,255,255,0.02)' }}
                        key={log.id} 
                        className="border-b border-white/5 last:border-0 transition-colors group"
                      >
                        <td className={rowPad}>
                          <span className={
                            log.action === 'Encrypt' ? 'text-sky-400' :
                            log.action === 'Decrypt' ? 'text-emerald-400' : 'text-rose-400'
                          }>
                            {log.action}
                          </span>
                        </td>
                        <td className={`${rowPad} font-medium text-slate-200 group-hover:text-white transition-colors`}>
                          {log.original_name || '—'}
                        </td>
                        <td className={`${rowPad} text-slate-400 text-sm`}>
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                        <td className={`${rowPad} text-right`}>
                          <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                            log.status === 'Success' 
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                              : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                          }`}>
                            {log.status}
                          </span>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {prefs.emailAlerts && (stats?.security_alerts ?? 0) > 0 && (
                <div className="mt-4 rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
                  {stats!.security_alerts} failed decrypt attempt{stats!.security_alerts === 1 ? '' : 's'} recorded. Check Analytics for details.
                </div>
              )}
            </Card>
          </motion.div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
};
