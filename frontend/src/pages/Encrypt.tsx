import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, ShieldCheck, Download, AlertTriangle, ArrowRight } from 'lucide-react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { DragDropZone } from '../components/ui/DragDropZone';
import { PasswordInput } from '../components/ui/PasswordInput';
import { PipelineVisualizer } from '../components/crypto/PipelineVisualizer';
import { fileService, type FileResponseDTO } from '../services/file.service';
import { transformPassword } from '@/crypto/aryabhata';
import {
  activateStep,
  buildEncryptSteps,
  failActiveStep,
  fillEncryptPipeline,
  type PipelineStep,
} from '@/crypto/pipeline';

const ENCRYPT_PLAYBACK = ['salt', 'pbkdf2', 'aes', 'pack'] as const;

export const Encrypt: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState<'idle' | 'encrypting' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [result, setResult] = useState<FileResponseDTO | null>(null);
  const [steps, setSteps] = useState<PipelineStep[]>([]);
  const [loadingText, setLoadingText] = useState('Initializing cryptographic engine...');
  const playRef = useRef<number | null>(null);

  const stopPlayback = () => {
    if (playRef.current) {
      window.clearInterval(playRef.current);
      playRef.current = null;
    }
  };

  const handleEncrypt = async () => {
    if (!file || !password) return;

    let pipelineSteps: PipelineStep[];
    try {
      const prep = transformPassword(password);
      pipelineSteps = buildEncryptSteps(prep, file.name, file.size);
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(err?.message || 'Password preprocessing failed.');
      return;
    }

    setSteps(pipelineSteps);
    setStatus('encrypting');
    setProgress(12);
    setErrorMessage('');
    setLoadingText('Aryabhata: password → numeric seed → phonetic stream');

    let playIndex = 0;
    playRef.current = window.setInterval(() => {
      const id = ENCRYPT_PLAYBACK[Math.min(playIndex, ENCRYPT_PLAYBACK.length - 1)];
      setSteps((prev) => activateStep(prev, id));
      setProgress((p) => Math.min(92, p + 10));
      if (id === 'salt') setLoadingText('Generating 16-byte salt + 12-byte nonce...');
      if (id === 'pbkdf2') setLoadingText('PBKDF2-HMAC-SHA256 (600,000 iterations) from AryaCrypt stream...');
      if (id === 'aes') setLoadingText('Streaming AES-256-GCM + auth tag...');
      if (id === 'pack') setLoadingText('Packing ARYA header + ciphertext into .arya...');
      playIndex += 1;
    }, 850);

    try {
      const response = await fileService.encryptFile(file, password);
      stopPlayback();
      setProgress(100);
      setLoadingText('Vault write complete.');
      if (response.pipeline) {
        setSteps(fillEncryptPipeline(pipelineSteps, response.pipeline));
      } else {
        setSteps(pipelineSteps.map((s) => ({ ...s, status: 'done' as const })));
      }
      setResult(response);
      setStatus('success');
    } catch (err: any) {
      stopPlayback();
      setStatus('error');
      setSteps((prev) => failActiveStep(prev, err.response?.data?.detail || 'Encryption failed.'));
      setErrorMessage(err.response?.data?.detail || 'Encryption failed due to an unknown error.');
    }
  };

  const resetState = () => {
    stopPlayback();
    setFile(null);
    setPassword('');
    setStatus('idle');
    setProgress(0);
    setResult(null);
    setSteps([]);
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
      <div className="max-w-3xl mx-auto flex flex-col gap-8 pb-12">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white flex items-center justify-center gap-3">
            <Lock className="w-8 h-8 text-sky-400" />
            Secure Encryption
          </h1>
          <p className="text-slate-400 max-w-xl mx-auto">
            Upload files for encryption with AES-256-GCM after AryaCrypt password
            preprocessing and PBKDF2-HMAC-SHA256 key derivation.
          </p>
          <p className="text-xs font-mono text-slate-600">ARYACRYPT v1.1.0</p>
        </div>

        <AnimatePresence mode="wait">
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

          {status === 'encrypting' && (
            <motion.div key="encrypting" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <PipelineVisualizer
                title="Encryption pipeline"
                subtitle={loadingText}
                steps={steps}
                progress={progress}
                accent="sky"
                footer="password -> NFC -> Aryabhata stream -> PBKDF2 -> AES-256-GCM -> .arya"
              />
            </motion.div>
          )}

          {status === 'success' && result && (
            <motion.div
              key="success"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-6"
            >
              <Card className="p-8 w-full flex flex-col items-center text-center border-emerald-500/30 bg-emerald-500/5">
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

              {steps.length > 0 && (
                <PipelineVisualizer
                  title="How this file was encrypted"
                  steps={steps}
                  progress={100}
                  accent="sky"
                  footer="password -> NFC -> Aryabhata stream -> PBKDF2 -> AES-256-GCM -> .arya"
                />
              )}
            </motion.div>
          )}

          {status === 'error' && (
            <motion.div key="error" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col gap-6">
              {steps.length > 0 && (
                <PipelineVisualizer title="Encryption pipeline" steps={steps} accent="sky" />
              )}
              <Card className="p-8 w-full flex flex-col items-center text-center border-rose-500/30 bg-rose-500/5">
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
