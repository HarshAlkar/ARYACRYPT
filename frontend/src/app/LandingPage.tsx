import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { BrandLockup } from '@/components/brand/BrandLockup';
import { BRAND, PRODUCT_NAME_DISPLAY } from '@/brand/constants';

const fade = { initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0 } };

export const LandingPage: React.FC = () => {
  return (
    <div className="relative isolate overflow-hidden">
      {/* Hero */}
      <section className="container mx-auto px-4 pt-20 pb-24 sm:pt-28 lg:pt-32">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            {...fade}
            transition={{ duration: 0.5 }}
            className="flex justify-center"
          >
            <BrandLockup variant="hero" to={null} />
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.15 }}
            className="mt-8 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed"
          >
            A password preprocessing and key-generation framework that integrates
            Aryabhata-inspired linguistic diffusion with PBKDF2-HMAC-SHA256 and
            AES-256-GCM — without replacing established cryptographic primitives.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.25 }}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3"
          >
            <Link
              to="/register"
              className="w-full sm:w-auto bg-primary text-primary-foreground font-semibold px-8 py-3 rounded-lg hover:bg-primary/90 transition-colors"
            >
              Start Encrypting
            </Link>
            <a
              href="#framework"
              className="w-full sm:w-auto bg-transparent text-slate-200 border border-border font-semibold px-8 py-3 rounded-lg hover:border-slate-500 transition-colors"
            >
              Explore Framework
            </a>
          </motion.div>
        </div>
      </section>

      {/* What is AryaCrypt */}
      <section id="framework" className="border-t border-border/50 py-20">
        <div className="container mx-auto px-4 max-w-3xl">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">What is AryaCrypt?</h2>
          <p className="text-slate-400 leading-relaxed">
            {PRODUCT_NAME_DISPLAY} is a cryptographic security framework that transforms
            a password through an Aryabhata-inspired RomanMapper pipeline before key
            derivation. The resulting stream feeds standard PBKDF2-HMAC-SHA256 (600,000
            iterations), which produces the key for AES-256-GCM file encryption. Output
            is packaged in the portable <span className="font-mono text-slate-300">.arya</span> container format.
          </p>
        </div>
      </section>

      {/* How it works */}
      <section className="border-t border-border/40 py-20 bg-card/20">
        <div className="container mx-auto px-4 max-w-3xl">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">How it works</h2>
          <ol className="space-y-4 text-slate-400 list-decimal list-inside leading-relaxed">
            <li>
              <span className="text-slate-200 font-medium">Preprocess</span> — Unicode NFC
              normalization and Aryabhata Base-100 phonetic diffusion (RomanMapper).
            </li>
            <li>
              <span className="text-slate-200 font-medium">Derive</span> — PBKDF2-HMAC-SHA256
              with a random 16-byte salt (600,000 iterations, 32-byte key).
            </li>
            <li>
              <span className="text-slate-200 font-medium">Encrypt</span> — AES-256-GCM with a
              random 12-byte nonce; authenticated ciphertext and tag.
            </li>
            <li>
              <span className="text-slate-200 font-medium">Package</span> — Serialize metadata
              and ciphertext into a versioned <span className="font-mono text-slate-300">.arya</span> file.
            </li>
          </ol>
        </div>
      </section>

      {/* Security architecture */}
      <section className="border-t border-border/40 py-20">
        <div className="container mx-auto px-4 max-w-3xl">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">Security architecture</h2>
          <p className="text-slate-400 leading-relaxed mb-4">
            AryaCrypt does not invent a new cipher. It adds a deterministic preprocessing
            layer ahead of well-studied primitives so that key material is derived from a
            transformed password stream rather than raw UTF-8 password bytes (for the
            current Aryabhata algorithm path).
          </p>
          <ul className="space-y-2 text-slate-400 text-sm">
            <li className="flex gap-2"><span className="text-sky-400/80">•</span> Authenticated encryption: AES-256-GCM</li>
            <li className="flex gap-2"><span className="text-sky-400/80">•</span> Key derivation: PBKDF2-HMAC-SHA256 (600k iterations)</li>
            <li className="flex gap-2"><span className="text-sky-400/80">•</span> Fresh salt and nonce per encryption</li>
            <li className="flex gap-2"><span className="text-sky-400/80">•</span> Spec v{BRAND.version} with cross-language test vectors</li>
          </ul>
        </div>
      </section>

      {/* SDKs + Web */}
      <section className="border-t border-border/40 py-20 bg-card/20">
        <div className="container mx-auto px-4 max-w-5xl">
          <h2 className="text-2xl font-bold text-slate-100 mb-8 text-center">Platforms</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Python SDK',
                body: 'pip install aryacrypt — encrypt and decrypt .arya files with full Spec v1.1.0 compatibility.',
              },
              {
                title: 'Node.js SDK',
                body: 'npm install aryacrypt — TypeScript SDK sharing the same format and vectors as Python.',
              },
              {
                title: 'Web platform',
                body: 'Authenticated vault for encrypt, decrypt, storage, analytics, and account settings.',
              },
            ].map((card) => (
              <div
                key={card.title}
                className="border border-border/60 rounded-lg p-6 bg-background/40"
              >
                <h3 className="text-lg font-semibold text-slate-100 mb-2">{card.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{card.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Research + stack */}
      <section className="border-t border-border/40 py-20">
        <div className="container mx-auto px-4 max-w-3xl space-y-10">
          <div>
            <h2 className="text-2xl font-bold text-slate-100 mb-4">Research contribution</h2>
            <p className="text-slate-400 leading-relaxed">
              AryaCrypt explores historical Aryabhata alphasyllabic encoding as a software
              diffusion step before modern KDF usage — bridging research on classical Indian
              mathematics with practical file encryption tooling. See the monorepo{' '}
              <span className="font-mono text-slate-300 text-sm">research/</span> and{' '}
              <span className="font-mono text-slate-300 text-sm">docs/spec/</span> materials.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-100 mb-4">Technology stack</h2>
            <p className="text-slate-400 leading-relaxed text-sm">
              React + Vite frontend · FastAPI + PostgreSQL backend · Official Python and
              Node SDKs · Spec v{BRAND.version} test vectors · Cross-language compatibility checks
            </p>
          </div>
        </div>
      </section>

    </div>
  );
};
