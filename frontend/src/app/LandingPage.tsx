import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, Zap, FileKey } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  {
    icon: <Lock className="h-6 w-6 text-primary" />,
    title: "Unbreakable AES-256",
    description: "Industry standard authenticated encryption backed by Galois/Counter Mode."
  },
  {
    icon: <FileKey className="h-6 w-6 text-accent" />,
    title: "Aryabhata Framework",
    description: "Novel mathematical diffusion mapping numeric seeds into complex phonetic entropy."
  },
  {
    icon: <Shield className="h-6 w-6 text-primary" />,
    title: "Zero-Knowledge",
    description: "Your keys never leave your device. Complete cryptographic privacy."
  },
  {
    icon: <Zap className="h-6 w-6 text-accent" />,
    title: "Lightning Fast",
    description: "Optimized asynchronous processing via modern backend technologies."
  }
];

export const LandingPage: React.FC = () => {
  return (
    <div className="relative isolate overflow-hidden min-h-[calc(100vh-4rem)]">
      {/* Background glow effects */}
      <div className="absolute top-0 -z-10 h-full w-full bg-background overflow-hidden">
        <div className="absolute bottom-auto left-auto right-10 top-10 h-[400px] w-[400px] rounded-full bg-primary/15 blur-[100px] animate-pulse"></div>
        <div className="absolute top-auto bottom-10 left-10 h-[300px] w-[300px] rounded-full bg-accent/15 blur-[100px]"></div>
      </div>

      <div className="container mx-auto px-4 pt-24 pb-20 sm:pt-32 lg:pt-40">
        <div className="text-center max-w-4xl mx-auto">
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="text-4xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl mb-6"
          >
            The Future of Encryption, <br className="hidden sm:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              Rooted in History.
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg sm:text-xl text-gray-400 mb-10 max-w-2xl mx-auto"
          >
            AryaCrypt merges the ancient Aryabhata mathematical numbering system with modern AES-256-GCM to deliver unparalleled file security.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link to="/register" className="w-full sm:w-auto bg-primary text-primary-foreground font-semibold px-8 py-3 rounded-lg hover:bg-primary/90 transition-all shadow-[0_0_20px_rgba(34,197,94,0.4)] hover:shadow-[0_0_30px_rgba(34,197,94,0.6)]">
              Start Encrypting
            </Link>
            <a href="#features" className="w-full sm:w-auto bg-card text-card-foreground border border-border font-semibold px-8 py-3 rounded-lg hover:border-gray-600 transition-colors">
              Learn More
            </a>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="container mx-auto px-4 py-24 border-t border-border/50 relative z-10 bg-background/50 backdrop-blur-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div 
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true, margin: "-100px" }}
              className="bg-card/50 backdrop-blur-md border border-border rounded-xl p-6 hover:border-primary/50 transition-all group hover:-translate-y-1"
            >
              <div className="mb-4 bg-background w-12 h-12 rounded-lg flex items-center justify-center border border-border group-hover:border-primary/50 transition-colors">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-100">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};
