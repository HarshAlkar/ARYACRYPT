import React from 'react';
import { Card } from './card';
import type { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface StatBoxProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  color?: 'cyan' | 'purple' | 'green' | 'red';
}

export const StatBox: React.FC<StatBoxProps> = ({ title, value, icon: Icon, trend, color = 'cyan' }) => {
  const colorMap = {
    cyan: 'text-sky-400 group-hover:text-sky-300',
    purple: 'text-purple-400 group-hover:text-purple-300',
    green: 'text-emerald-400 group-hover:text-emerald-300',
    red: 'text-rose-400 group-hover:text-rose-300'
  };

  const bgMap = {
    cyan: 'bg-sky-500/10 group-hover:bg-sky-500/20',
    purple: 'bg-purple-500/10 group-hover:bg-purple-500/20',
    green: 'bg-emerald-500/10 group-hover:bg-emerald-500/20',
    red: 'bg-rose-500/10 group-hover:bg-rose-500/20'
  };

  return (
    <Card hoverEffect className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        <motion.div 
          whileHover={{ rotate: 15 }}
          className={`p-3 rounded-lg transition-colors ${bgMap[color]}`}
        >
          <Icon className={`w-5 h-5 ${colorMap[color]}`} />
        </motion.div>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-3xl font-bold tracking-tight text-slate-50 text-glow">{value}</span>
        {trend && (
          <span className="text-xs font-medium text-emerald-400 mt-1">
            {trend} vs prior week
          </span>
        )}
      </div>
    </Card>
  );
};
