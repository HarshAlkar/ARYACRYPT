import React from 'react';
import { motion } from 'framer-motion';
import { BrandLockup } from '@/components/brand/BrandLockup';
import { Link } from 'react-router-dom';

/** Alternate hero (not mounted). Kept accurate for reuse. */
export const HeroSection: React.FC = () => {
  return (
    <section className="relative min-h-[70vh] flex items-center justify-center pt-16">
      <div className="relative z-10 max-w-3xl mx-auto px-6 flex flex-col items-center text-center">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <BrandLockup variant="hero" to={null} />
        </motion.div>
        <p className="mt-8 text-slate-400 max-w-xl">
          Password preprocessing and key generation for AES-256-GCM file encryption —
          Spec v1.1.0.
        </p>
        <div className="mt-8 flex gap-3">
          <Link
            to="/register"
            className="bg-primary text-primary-foreground font-semibold px-6 py-2.5 rounded-lg"
          >
            Start Encrypting
          </Link>
          <a href="#framework" className="border border-border px-6 py-2.5 rounded-lg text-slate-200">
            Explore Framework
          </a>
        </div>
      </div>
    </section>
  );
};
