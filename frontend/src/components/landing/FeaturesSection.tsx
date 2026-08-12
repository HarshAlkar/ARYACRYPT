import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, Binary, Fingerprint, Layers } from 'lucide-react';

export const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: "AES-256-GCM Core",
      description: "Military-grade encryption leveraging Galois/Counter Mode for high-speed authenticated encryption, ensuring both data confidentiality and authenticity.",
      icon: ShieldAlert,
      delay: 0.1
    },
    {
      title: "Linguistic Obfuscation",
      description: "Data is mapped to ancient Roman numerals and diffused through the Aryabhata positional algorithm, preventing statistical and pattern analysis.",
      icon: Binary,
      delay: 0.2
    },
    {
      title: "PBKDF2 Key Derivation",
      description: "Passwords are mathematically stretched using HMAC-SHA256 with 600,000 iterations and a cryptographically secure 16-byte salt.",
      icon: Fingerprint,
      delay: 0.3
    },
    {
      title: "Zero Metadata Leakage",
      description: "The custom .arya file format securely embeds encrypted nonces, salts, and authentication tags in a proprietary binary header structure.",
      icon: Layers,
      delay: 0.4
    }
  ];

  return (
    <section className="py-24 relative overflow-hidden bg-black/40">
      
      {/* Decorative Grid */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-20"
        style={{ backgroundImage: 'radial-gradient(circle at right center, rgba(14, 165, 233, 0.1) 0%, transparent 50%)' }} 
      />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl font-bold text-slate-100 mb-4"
          >
            Cryptographic Architecture
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-slate-400 max-w-2xl mx-auto text-lg"
          >
            Built on a foundation of proven standards, mathematically enhanced to withstand modern computational attacks.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: feature.delay, duration: 0.5 }}
              whileHover={{ y: -5 }}
              className="bg-card/40 backdrop-blur-md border border-white/5 rounded-2xl p-8 hover:border-sky-500/30 hover:shadow-[0_0_30px_rgba(14,165,233,0.15)] transition-all group"
            >
              <div className="w-14 h-14 bg-white/5 rounded-xl flex items-center justify-center mb-6 group-hover:bg-sky-500/10 group-hover:scale-110 transition-all shadow-inner">
                <feature.icon className="w-7 h-7 text-sky-400 group-hover:text-yellow-500 transition-colors" />
              </div>
              <h3 className="text-xl font-bold text-slate-200 mb-3 group-hover:text-white">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed group-hover:text-slate-300">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
