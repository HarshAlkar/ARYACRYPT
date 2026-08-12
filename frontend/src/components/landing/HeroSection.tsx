import React from 'react';
import { motion } from 'framer-motion';
import { Shield, ChevronRight, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const HeroSection: React.FC = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      
      {/* Background Ornaments (Sacred Geometry / Cyber) */}
      <div className="absolute inset-0 z-0 pointer-events-none flex items-center justify-center opacity-40">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 150, repeat: Infinity, ease: "linear" }}
          className="w-[800px] h-[800px] border border-yellow-500/20 rounded-full flex items-center justify-center relative"
        >
          {/* Decorative nodes */}
          <div className="absolute top-0 w-2 h-2 bg-yellow-500 rounded-full shadow-[0_0_10px_rgba(234,179,8,0.8)] -mt-1" />
          <div className="absolute bottom-0 w-2 h-2 bg-sky-500 rounded-full shadow-[0_0_10px_rgba(14,165,233,0.8)] -mb-1" />
          
          <div className="w-[600px] h-[600px] border border-sky-500/20 rounded-full flex items-center justify-center rotate-45">
            <div className="w-[400px] h-[400px] border border-purple-500/20 rounded-full flex items-center justify-center border-dashed" />
          </div>
        </motion.div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
        
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-yellow-500/30 text-yellow-500 text-sm font-medium mb-8 backdrop-blur-md shadow-[0_0_15px_rgba(234,179,8,0.2)]"
        >
          <Shield className="w-4 h-4" />
          <span>Next-Generation Cryptographic Framework</span>
        </motion.div>

        {/* Headline */}
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-5xl md:text-7xl font-bold tracking-tight text-slate-100 mb-6 max-w-4xl"
        >
          Where Ancient Mathematics Meets <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-purple-500 to-yellow-500 text-glow-gold">
            Modern Security.
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10"
        >
          AryaCrypt merges Aryabhata's positional notation with AES-256-GCM to create a linguistically obfuscated, mathematically impenetrable encryption standard.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center gap-4"
        >
          <button 
            onClick={() => navigate('/encrypt')}
            className="group flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-500 hover:to-yellow-400 text-slate-900 font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(234,179,8,0.4)] hover:shadow-[0_0_30px_rgba(234,179,8,0.6)]"
          >
            <Lock className="w-5 h-5" />
            Secure Your Data
          </button>
          <button 
            className="group flex items-center gap-2 px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-slate-200 font-medium transition-all"
          >
            Read the Research
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>

      </div>
      
      {/* Scroll indicator */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <span className="text-xs text-slate-500 uppercase tracking-widest font-semibold">Discover</span>
        <motion.div 
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          className="w-px h-12 bg-gradient-to-b from-yellow-500/50 to-transparent"
        />
      </motion.div>
    </section>
  );
};
