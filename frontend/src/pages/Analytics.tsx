import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { LineChart as LineChartIcon, Activity, BarChart2, Cpu, ShieldCheck, Zap } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, ScatterChart, Scatter, ZAxis, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { fileService, type VaultStats } from '../services/file.service';

const SUCCESS_COLORS = ['#38bdf8', '#fb7185'];

export const Analytics: React.FC = () => {
  const [stats, setStats] = useState<VaultStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await fileService.getStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  const fileSizeData = useMemo(
    () => (stats?.daily_volume ?? []).map((d) => ({ date: d.date, size: d.size_mb })),
    [stats]
  );

  const volumeData = useMemo(
    () => (stats?.daily_ops ?? []).map((d) => ({ date: d.date, count: d.count })),
    [stats]
  );

  const processingData = useMemo(
    () =>
      (stats?.processing ?? []).map((p, idx) => ({
        id: String(idx),
        sizeMB: p.size_mb,
        timeMs: p.time_ms,
      })),
    [stats]
  );

  const successData = useMemo(() => {
    const success = stats?.success_rate.success ?? 0;
    const failure = stats?.success_rate.failure ?? 0;
    if (success === 0 && failure === 0) {
      return [
        { name: 'Successful Ops', value: 0 },
        { name: 'Failed Ops', value: 0 },
      ];
    }
    return [
      { name: 'Successful Ops', value: success },
      { name: 'Failed Ops', value: failure },
    ];
  }, [stats]);

  const successPct =
    successData[0].value + successData[1].value === 0
      ? 100
      : Math.round((successData[0].value / (successData[0].value + successData[1].value)) * 100);

  // Derive radar scores from real telemetry (bounded 0–100)
  const frameworkData = useMemo(() => {
    const totalOps = (stats?.success_rate.success ?? 0) + (stats?.success_rate.failure ?? 0);
    const integrity = totalOps === 0 ? 100 : successPct;
    const avgMs =
      processingData.length > 0
        ? processingData.reduce((a, p) => a + p.timeMs, 0) / processingData.length
        : 0;
    const throughput = avgMs === 0 ? 80 : Math.max(20, Math.min(100, Math.round(100 - avgMs / 50)));
    const volumeScore = Math.min(100, Math.round(((stats?.total_files ?? 0) / 10) * 100));
    const decryptShare =
      (stats?.total_encrypted ?? 0) === 0
        ? 50
        : Math.min(100, Math.round(((stats?.total_decrypted ?? 0) / Math.max(stats!.total_encrypted, 1)) * 100));

    return [
      { subject: 'Throughput', A: throughput, fullMark: 100 },
      { subject: 'Vault Usage', A: Math.max(10, volumeScore), fullMark: 100 },
      { subject: 'Crypto Strength', A: 100, fullMark: 100 },
      { subject: 'Integrity', A: integrity, fullMark: 100 },
      { subject: 'Decrypt Rate', A: Math.max(10, decryptShare), fullMark: 100 },
      { subject: 'Alert Health', A: Math.max(0, 100 - Math.min(100, (stats?.security_alerts ?? 0) * 10)), fullMark: 100 },
    ];
  }, [stats, processingData, successPct]);

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto flex flex-col gap-6 h-full min-h-[calc(100vh-8rem)]">
        <div className="flex items-center gap-3 mb-2">
          <LineChartIcon className="w-8 h-8 text-sky-400" />
          <div>
            <h1 className="text-3xl font-bold text-white">Analytics</h1>
            <p className="text-slate-400 mt-1">Encryption, decryption, and vault telemetry from your account.</p>
            <p className="text-xs font-mono text-slate-600 mt-1">ARYACRYPT v1.1.0</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card hoverEffect className="p-6 h-[400px] flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-sky-400" />
                  <h2 className="text-lg font-semibold text-slate-100">Daily Encryption Volume</h2>
                </div>
                <span className="text-xs font-medium bg-sky-500/10 text-sky-400 px-2.5 py-1 rounded-full border border-sky-500/20">
                  Last 7 Days
                </span>
              </div>
              <div className="flex-1 w-full h-full min-h-0">
                {isLoading ? (
                  <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 gap-3">
                    <div className="w-8 h-8 border-2 border-sky-400/20 border-t-sky-400 rounded-full animate-spin" />
                    <span>Loading telemetry...</span>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={fileSizeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorSize" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.5}/>
                          <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                      <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val.toFixed(1)} MB`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                        itemStyle={{ color: '#38bdf8', fontWeight: 500 }}
                        formatter={(value) => [`${Number(value ?? 0).toFixed(2)} MB`, 'Volume']}
                      />
                      <Area type="monotone" dataKey="size" stroke="#38bdf8" strokeWidth={2} fillOpacity={1} fill="url(#colorSize)" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card hoverEffect className="p-6 h-[400px] flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-purple-400" />
                  <h2 className="text-lg font-semibold text-slate-100">Operation Frequency</h2>
                </div>
                <span className="text-xs font-medium bg-purple-500/10 text-purple-400 px-2.5 py-1 rounded-full border border-purple-500/20">
                  Encrypt + Decrypt
                </span>
              </div>
              <div className="flex-1 w-full h-full min-h-0">
                {isLoading ? (
                  <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 gap-3">
                    <div className="w-8 h-8 border-2 border-purple-400/20 border-t-purple-400 rounded-full animate-spin" />
                    <span>Loading telemetry...</span>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={volumeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                      <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                        itemStyle={{ color: '#a855f7', fontWeight: 500 }}
                        formatter={(value) => [`${Number(value ?? 0)} ops`, 'Operations']}
                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                      />
                      <Bar dataKey="count" fill="#a855f7" radius={[4, 4, 0, 0]} barSize={30} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="lg:col-span-2">
            <Card hoverEffect className="p-6 h-[400px] flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-emerald-400" />
                  <h2 className="text-lg font-semibold text-slate-100">Cryptographic Processing Performance</h2>
                </div>
                <span className="text-xs font-medium bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full border border-emerald-500/20">
                  Measured duration_ms
                </span>
              </div>
              <div className="flex-1 w-full h-full min-h-0">
                {isLoading ? (
                  <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 gap-3">
                    <div className="w-8 h-8 border-2 border-emerald-400/20 border-t-emerald-400 rounded-full animate-spin" />
                    <span>Analyzing performance telemetry...</span>
                  </div>
                ) : processingData.length === 0 ? (
                  <div className="w-full h-full flex items-center justify-center text-slate-500">
                    No processing telemetry yet — encrypt or decrypt a file to populate this chart.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: -20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis type="number" dataKey="sizeMB" name="File Size" unit=" MB" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                      <YAxis type="number" dataKey="timeMs" name="Processing Time" unit=" ms" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                      <ZAxis type="number" range={[50, 50]} />
                      <Tooltip
                        cursor={{ strokeDasharray: '3 3', stroke: 'rgba(255,255,255,0.1)' }}
                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                        itemStyle={{ color: '#34d399', fontWeight: 500 }}
                      />
                      <Scatter name="Ops" data={processingData} fill="#34d399" opacity={0.6} />
                    </ScatterChart>
                  </ResponsiveContainer>
                )}
              </div>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card hoverEffect className="p-6 h-[400px] flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-sky-400" />
                  <h2 className="text-lg font-semibold text-slate-100">Operation Success Rate</h2>
                </div>
              </div>
              <div className="flex-1 w-full h-full min-h-0 relative flex flex-col items-center justify-center">
                {isLoading ? (
                  <div className="text-slate-500">Loading...</div>
                ) : successData[0].value + successData[1].value === 0 ? (
                  <div className="text-slate-500">No operations recorded yet.</div>
                ) : (
                  <>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={successData}
                          cx="50%"
                          cy="50%"
                          innerRadius={80}
                          outerRadius={120}
                          paddingAngle={5}
                          dataKey="value"
                          stroke="none"
                        >
                          {successData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={SUCCESS_COLORS[index % SUCCESS_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                          itemStyle={{ color: '#fff' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                      <span className="text-4xl font-bold text-white">{successPct}%</span>
                      <span className="text-sm text-slate-400">Success</span>
                    </div>
                  </>
                )}
              </div>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Card hoverEffect className="p-6 h-[400px] flex flex-col">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-amber-400" />
                  <h2 className="text-lg font-semibold text-slate-100">Vault Health Profile</h2>
                </div>
              </div>
              <div className="flex-1 w-full h-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={frameworkData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="AryaCrypt" dataKey="A" stroke="#fbbf24" strokeWidth={2} fill="#fbbf24" fillOpacity={0.3} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      itemStyle={{ color: '#fbbf24' }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </DashboardLayout>
  );
};
