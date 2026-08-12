import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { HardDrive, ShieldAlert, FileKey2, Activity, Lock, Unlock, Loader2 } from 'lucide-react';
import { StatBox } from '../components/ui/StatBox';
import { Card } from '../components/ui/Card';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { fileService, type FileResponseDTO } from '../services/file.service';

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 300 } }
};

export const Dashboard: React.FC = () => {
  const [files, setFiles] = useState<FileResponseDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await fileService.getHistory();
        setFiles(history);
      } catch (error) {
        console.error("Failed to fetch history:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const totalFiles = files.length;
  // Mocked for now until backend supports these models
  const totalDecrypted = 0;
  const securityAlerts = 0;

  const stats = [
    { title: "Total Files Secured", value: totalFiles.toString(), icon: FileKey2, color: "cyan" as const, trend: "+12%" },
    { title: "Total Encrypted", value: totalFiles.toString(), icon: Lock, color: "purple" as const, trend: "+5%" },
    { title: "Total Decrypted", value: totalDecrypted.toString(), icon: Unlock, color: "green" as const, trend: "-2%" },
    { title: "Security Alerts", value: securityAlerts.toString(), icon: ShieldAlert, color: "red" as const },
  ];

  const recentActivity = files.slice(0, 5).map(file => ({
    id: file.id,
    action: "Encrypted",
    file: file.original_name,
    time: new Date(file.created_at).toLocaleDateString(),
    status: "Success"
  }));

  const storageUsedBytes = files.reduce((acc, f) => acc + f.file_size_bytes, 0);
  const storageUsedGB = (storageUsedBytes / (1024 ** 3)).toFixed(2);
  const capacityGB = 250.0;
  const storagePercentage = Math.min(100, Math.round((storageUsedBytes / (capacityGB * 1024 ** 3)) * 100));

  return (
    <DashboardLayout>
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="max-w-7xl mx-auto flex flex-col gap-8"
      >
        
        {/* Top Analytics Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, i) => (
            <motion.div key={i} variants={itemVariants}>
              <StatBox {...stat} />
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Storage Usage Visual Analytics */}
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <Card hoverEffect className="h-full flex flex-col">
              <div className="flex items-center gap-3 mb-6">
                <HardDrive className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-slate-100">Vault Storage</h2>
              </div>
              
              <div className="flex-1 flex flex-col justify-center gap-8 py-6">
                <div className="relative flex justify-center items-center">
                  {/* Decorative glowing rings representing storage bounds */}
                  <div className="absolute w-40 h-40 rounded-full border-4 border-white/5"></div>
                  <div className="absolute w-40 h-40 rounded-full border-4 border-purple-500/20 border-t-purple-500 animate-[spin_3s_linear_infinite]"></div>
                  <div className="flex flex-col items-center justify-center relative z-10">
                    <span className="text-3xl font-bold text-glow">{storagePercentage}<span className="text-xl text-slate-400">%</span></span>
                    <span className="text-sm text-slate-400 mt-1">Allocated</span>
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
                    <span className="text-slate-500">Total Capacity</span>
                    <span className="font-medium text-slate-400">{capacityGB.toFixed(1)} GB</span>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Recent Cryptographic Activities */}
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <Card hoverEffect className="h-full">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-sky-400" />
                  <h2 className="text-lg font-semibold text-slate-100">Encryption History</h2>
                </div>
                <button className="text-sm font-medium text-sky-400 hover:text-sky-300 transition-colors">View All Logs</button>
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
                          Loading history...
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
                        className="border-b border-white/5 last:border-0 transition-colors group cursor-pointer"
                      >
                        <td className="py-4">
                          <span className={
                            log.action === 'Encrypted' ? 'text-sky-400' :
                            log.action === 'Decrypted' ? 'text-emerald-400' : 'text-rose-400'
                          }>
                            {log.action}
                          </span>
                        </td>
                        <td className="py-4 font-medium text-slate-200 group-hover:text-white transition-colors">{log.file}</td>
                        <td className="py-4 text-slate-400 text-sm">{log.time}</td>
                        <td className="py-4 text-right">
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
            </Card>
          </motion.div>
          
        </div>
      </motion.div>
    </DashboardLayout>
  );
};
