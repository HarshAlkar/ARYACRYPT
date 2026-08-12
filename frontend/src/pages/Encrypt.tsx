import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, ShieldCheck, Download, AlertTriangle, ArrowRight } from 'lucide-react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '../components/ui/Card';
import { DragDropZone } from '../components/ui/DragDropZone';
import { PasswordInput } from '../components/ui/PasswordInput';
import { fileService, type FileResponseDTO } from '../services/file.service';

export const Encrypt: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState<'idle' | 'encrypting' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [result, setResult] = useState<FileResponseDTO | null>(null);
  const [loadingText, setLoadingText] = useState("Initializing cryptographic engine...");

  const handleEncrypt = async () => {
    if (!file || !password) return;
    
    setStatus('encrypting');
    setProgress(0);
    setErrorMessage('');
    
    // Simulate progress steps for the visualizer
    const progressInterval = setInterval(() => {
      setProgress(p => {
        if (p < 15) {
          setLoadingText("Aryabhata: password → numeric seed...");
          return p + 4;
        }
        if (p < 35) {
          setLoadingText("Aryabhata: Base-100 Σ rᵢ·100ⁱ decomposition...");
          return p + 3;
        }
        if (p < 55) {
          setLoadingText("Aryabhata: Varga/Avarga Roman-Sanskrit mapping...");
          return p + 2;
        }
        if (p < 75) {
          setLoadingText("PBKDF2-HMAC-SHA256 (600k) from AryaCrypt stream...");
          return p + 1.5;
        }
        if (p < 95) {
          setLoadingText("Streaming AES-256-GCM + Auth Tag...");
          return p + 0.5;
        }
        return p;
      });
    }, 150);

    try {
      const response = await fileService.encryptFile(file, password);
      clearInterval(progressInterval);
      setProgress(100);
      setLoadingText("Finalizing secure vault storage...");
      
      // Brief delay for UX so they see 100%
      setTimeout(() => {
        setResult(response);
        setStatus('success');
      }, 600);
      
    } catch (err: any) {
      clearInterval(progressInterval);
      setStatus('error');
      setErrorMessage(err.response?.data?.detail || "Encryption failed due to an unknown error.");
    }
  };

  const resetState = () => {
    setFile(null);
    setPassword('');
    setStatus('idle');
    setProgress(0);
    setResult(null);
  };

  const handleDownload = async () => {
    if (!result) return;
    try {
      await fileService.downloadEncryptedFile(result.id, result.encrypted_name);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Download failed. Please try again from Vault.');
      setStatus('error');
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto flex flex-col gap-8 h-full min-h-[calc(100vh-8rem)] justify-center">
        
        <div className="text-center space-y-2 mb-4">
          <h1 className="text-3xl font-bold text-white flex items-center justify-center gap-3">
            <Lock className="w-8 h-8 text-sky-400" />
            Secure Encryption
          </h1>
          <p className="text-slate-400 max-w-xl mx-auto">
            Upload your sensitive files and protect them using military-grade AES-256-GCM 
            backed by the phonetic AryaCrypt framework.
          </p>
        </div>

        <AnimatePresence mode="wait">
          
          {/* IDLE STATE */}
          {status === 'idle' && (
            <motion.div 
              key="idle"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              <div className="md:col-span-2">
                <DragDropZone onFileSelect={setFile} selectedFile={file} />
              </div>

              <AnimatePresence>
                {file && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="md:col-span-2 space-y-6 overflow-hidden"
                  >
                    <Card className="p-6">
                      <PasswordInput 
                        value={password} 
                        onChange={setPassword} 
                        showStrengthMeter={true} 
                        label="Encryption Password"
                        placeholder="Enter a strong password to lock this file..."
                      />
                    </Card>

                    <button
                      onClick={handleEncrypt}
                      disabled={!password || password.length < 8}
                      className="w-full py-4 rounded-xl font-bold text-white bg-gradient-to-r from-sky-500 to-purple-600 hover:from-sky-400 hover:to-purple-500 shadow-[0_0_20px_rgba(14,165,233,0.3)] hover:shadow-[0_0_30px_rgba(14,165,233,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg"
                    >
                      <Lock className="w-5 h-5" />
                      Encrypt Data Now
                    </button>
                    {password.length > 0 && password.length < 8 && (
                      <p className="text-amber-400/90 text-sm text-center">
                        Aryabhata requires at least 8 characters.
                      </p>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {/* ENCRYPTING STATE (Framework Visualization) */}
          {status === 'encrypting' && (
            <motion.div 
              key="encrypting"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              className="flex justify-center"
            >
              <Card className="p-12 flex flex-col items-center max-w-lg w-full text-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-b from-sky-500/5 to-transparent pointer-events-none" />
                
                <div className="relative w-32 h-32 flex items-center justify-center mb-8">
                  <div className="absolute inset-0 rounded-full border-2 border-slate-800" />
                  <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 rounded-full border-t-2 border-r-2 border-sky-400"
                  />
                  <motion.div 
                    animate={{ rotate: -360 }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-4 rounded-full border-b-2 border-l-2 border-purple-500"
                  />
                  <Lock className="w-10 h-10 text-sky-400 animate-pulse" />
                </div>

                <h3 className="text-xl font-bold text-slate-200 mb-2">Securing Payload</h3>
                <p className="text-sky-400 text-sm h-6 font-mono">{loadingText}</p>

                <div className="w-full bg-slate-800/50 rounded-full h-2 mt-8 overflow-hidden relative">
                  <motion.div 
                    className="absolute top-0 left-0 h-full bg-gradient-to-r from-sky-500 to-purple-500"
                    animate={{ width: `${progress}%` }}
                    transition={{ ease: "easeOut" }}
                  />
                </div>
                <div className="w-full flex justify-between text-xs text-slate-500 mt-2 font-mono">
                  <span>0%</span>
                  <span>{Math.round(progress)}%</span>
                </div>
              </Card>
            </motion.div>
          )}

          {/* SUCCESS STATE */}
          {status === 'success' && result && (
            <motion.div 
              key="success"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center"
            >
              <Card className="p-8 max-w-lg w-full flex flex-col items-center text-center border-emerald-500/30 bg-emerald-500/5">
                <div className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(16,185,129,0.3)]">
                  <ShieldCheck className="w-10 h-10 text-emerald-400" />
                </div>
                
                <h3 className="text-2xl font-bold text-emerald-400 mb-2">Encryption Successful</h3>
                <p className="text-slate-300 mb-8">
                  Your file has been secured and stored in the AryaCrypt vault.
                </p>

                <div className="w-full bg-black/40 rounded-lg p-4 mb-8 text-left space-y-3 border border-white/5">
                  <div className="flex justify-between">
                    <span className="text-slate-500 text-sm">Original File</span>
                    <span className="text-slate-200 text-sm font-medium truncate max-w-[200px]">{result.original_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 text-sm">Protected As</span>
                    <span className="text-emerald-400 text-sm font-mono truncate max-w-[200px]">{result.encrypted_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 text-sm">Vault ID</span>
                    <span className="text-slate-400 text-sm font-mono truncate max-w-[200px]">{result.id}</span>
                  </div>
                </div>

                <div className="w-full flex gap-4">
                  <button 
                    onClick={resetState}
                    className="flex-1 py-3 px-4 rounded-lg font-medium text-slate-300 bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
                  >
                    Encrypt Another
                  </button>
                  <button 
                    onClick={handleDownload}
                    className="flex-1 py-3 px-4 rounded-lg font-medium text-white bg-emerald-600 hover:bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.4)] transition-all flex items-center justify-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download .arya
                  </button>
                </div>
              </Card>
            </motion.div>
          )}

          {/* ERROR STATE */}
          {status === 'error' && (
            <motion.div 
              key="error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex justify-center"
            >
              <Card className="p-8 max-w-lg w-full flex flex-col items-center text-center border-rose-500/30 bg-rose-500/5">
                <div className="w-16 h-16 rounded-full bg-rose-500/20 flex items-center justify-center mb-6">
                  <AlertTriangle className="w-8 h-8 text-rose-400" />
                </div>
                
                <h3 className="text-xl font-bold text-rose-400 mb-2">Encryption Failed</h3>
                <p className="text-slate-300 mb-8">{errorMessage}</p>

                <button 
                  onClick={() => setStatus('idle')}
                  className="w-full py-3 rounded-lg font-medium text-white bg-rose-600 hover:bg-rose-500 transition-colors flex items-center justify-center gap-2"
                >
                  Try Again <ArrowRight className="w-4 h-4" />
                </button>
              </Card>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </DashboardLayout>
  );
};
