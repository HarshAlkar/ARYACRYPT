import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import type { PipelineStep } from '@/crypto/pipeline';

type Accent = 'sky' | 'emerald';

const accentClass: Record<Accent, { ring: string; text: string; bar: string; border: string }> = {
  sky: {
    ring: 'text-sky-400',
    text: 'text-sky-400',
    bar: 'bg-gradient-to-r from-sky-500 to-purple-500',
    border: 'border-sky-500/25',
  },
  emerald: {
    ring: 'text-emerald-400',
    text: 'text-emerald-400',
    bar: 'bg-gradient-to-r from-emerald-500 to-teal-500',
    border: 'border-emerald-500/25',
  },
};

function StepIcon({ status, accent }: { status: PipelineStep['status']; accent: Accent }) {
  if (status === 'done') return <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />;
  if (status === 'error') return <XCircle className="w-5 h-5 text-rose-400 shrink-0" />;
  if (status === 'active') return <Loader2 className={`w-5 h-5 shrink-0 animate-spin ${accentClass[accent].ring}`} />;
  return <Circle className="w-5 h-5 text-slate-600 shrink-0" />;
}

export const PipelineVisualizer: React.FC<{
  title: string;
  subtitle?: string;
  steps: PipelineStep[];
  progress?: number;
  accent?: Accent;
  footer?: string;
}> = ({ title, subtitle, steps, progress, accent = 'sky', footer }) => {
  const colors = accentClass[accent];
  const doneCount = steps.filter((s) => s.status === 'done').length;

  return (
    <Card className={`p-6 sm:p-8 w-full border ${colors.border}`}>
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-slate-100">{title}</h3>
          {subtitle && <p className={`text-sm font-mono mt-1 ${colors.text}`}>{subtitle}</p>}
        </div>
        <span className="text-xs font-mono text-slate-500 shrink-0">
          {doneCount}/{steps.length} steps
        </span>
      </div>

      {typeof progress === 'number' && (
        <div className="mb-6">
          <div className="w-full bg-slate-800/50 rounded-full h-1.5 overflow-hidden">
            <motion.div
              className={`h-full ${colors.bar}`}
              animate={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              transition={{ ease: 'easeOut' }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
            <span>pipeline</span>
            <span>{Math.round(progress)}%</span>
          </div>
        </div>
      )}

      <ol className="space-y-3">
        {steps.map((step, index) => {
          const dim = step.status === 'pending';
          return (
            <motion.li
              key={step.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.04 }}
              className={`rounded-lg border p-3 sm:p-4 ${
                step.status === 'error'
                  ? 'border-rose-500/30 bg-rose-500/5'
                  : step.status === 'active'
                    ? `${colors.border} bg-white/[0.03]`
                    : 'border-white/5 bg-black/20'
              } ${dim ? 'opacity-45' : 'opacity-100'}`}
            >
              <div className="flex items-start gap-3">
                <StepIcon status={step.status} accent={accent} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-slate-200">
                    <span className="font-mono text-slate-500 mr-2">[{index + 1}]</span>
                    {step.title}
                  </p>
                  {step.hint && <p className="text-xs text-slate-500 mt-1">{step.hint}</p>}
                  {step.rows.length > 0 && (step.status === 'done' || step.status === 'active' || step.status === 'error') && (
                    <dl className="mt-3 space-y-1.5 font-mono text-[11px] sm:text-xs">
                      {step.rows.map((row) => (
                        <div key={row.label} className="grid grid-cols-[7.5rem_1fr] sm:grid-cols-[9rem_1fr] gap-2">
                          <dt className="text-slate-500 truncate">{row.label}</dt>
                          <dd className="text-slate-300 break-all">{row.value}</dd>
                        </div>
                      ))}
                    </dl>
                  )}
                </div>
              </div>
            </motion.li>
          );
        })}
      </ol>

      {footer && (
        <p className="mt-6 text-center text-[11px] font-mono text-slate-500 break-all">{footer}</p>
      )}
    </Card>
  );
};
