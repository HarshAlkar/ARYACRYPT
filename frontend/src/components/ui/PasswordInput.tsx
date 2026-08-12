import React, { useState } from 'react';
import { Eye, EyeOff, Lock, KeyRound } from 'lucide-react';
import { motion } from 'framer-motion';

interface PasswordInputProps {
  value: string;
  onChange: (value: string) => void;
  showStrengthMeter?: boolean;
  label?: string;
  placeholder?: string;
}

export const PasswordInput: React.FC<PasswordInputProps> = ({ 
  value, 
  onChange, 
  showStrengthMeter = false,
  label = "Secure Password",
  placeholder = "Enter encryption key"
}) => {
  const [showPassword, setShowPassword] = useState(false);

  const getStrength = (pass: string) => {
    let score = 0;
    if (!pass) return { score: 0, label: '', color: 'bg-white/5' };
    if (pass.length > 8) score += 1;
    if (/[A-Z]/.test(pass)) score += 1;
    if (/[0-9]/.test(pass)) score += 1;
    if (/[^A-Za-z0-9]/.test(pass)) score += 1;

    if (score <= 1) return { score, label: 'Weak', color: 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]' };
    if (score === 2) return { score, label: 'Fair', color: 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' };
    if (score === 3) return { score, label: 'Good', color: 'bg-sky-500 shadow-[0_0_8px_rgba(14,165,233,0.5)]' };
    return { score, label: 'Strong', color: 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' };
  };

  const strength = getStrength(value);

  return (
    <div className="w-full flex flex-col gap-2">
      {label && (
        <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
          <KeyRound className="w-4 h-4 text-sky-400" />
          {label}
        </label>
      )}
      
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Lock className="h-5 w-5 text-slate-400 group-focus-within:text-sky-400 transition-colors" />
        </div>
        
        <input
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-black/20 border border-white/10 rounded-lg pl-11 pr-12 py-3 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500/50 transition-all"
          placeholder={placeholder}
        />
        
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-200 transition-colors"
          title={showPassword ? "Hide Password" : "Show Password"}
        >
          {showPassword ? (
            <EyeOff className="h-5 w-5" />
          ) : (
            <Eye className="h-5 w-5" />
          )}
        </button>
      </div>

      {showStrengthMeter && value.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-2 space-y-2 overflow-hidden"
        >
          <div className="flex justify-between text-xs font-medium">
            <span className="text-slate-400">Security Level</span>
            <span className={`transition-colors duration-300 ${
              strength.score <= 1 ? 'text-rose-400' :
              strength.score === 2 ? 'text-amber-400' :
              strength.score === 3 ? 'text-sky-400' : 'text-emerald-400'
            }`}>
              {strength.label}
            </span>
          </div>
          <div className="flex gap-1 h-1.5 w-full">
            {[1, 2, 3, 4].map((level) => (
              <div 
                key={level}
                className={`flex-1 rounded-full transition-all duration-500 ${
                  level <= strength.score ? strength.color : 'bg-white/5'
                }`}
              />
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};
