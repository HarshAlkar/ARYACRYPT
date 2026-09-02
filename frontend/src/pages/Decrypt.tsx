import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Unlock, FileCheck, Download, AlertTriangle, ArrowRight, HardDrive, X } from 'lucide-react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { DragDropZone } from '../components/ui/DragDropZone';
import { PasswordInput } from '../components/ui/PasswordInput';
import { PipelineVisualizer } from '../components/crypto/PipelineVisualizer';
import { fileService, type FileResponseDTO } from '../services/file.service';
import { transformPassword } from '@/crypto/aryabhata';
import { parseAryaHeader } from '@/crypto/aryaContainer';
import {
  activateStep,
  buildDecryptSteps,
  completeDecryptPipeline,
  failActiveStep,
  fillDecryptHeader,
  type PipelineStep,
} from '@/crypto/pipeline';

export type VaultDecryptState = {
  vaultFile: Pick<FileResponseDTO, 'id' | 'original_name' | 'encrypted_name'>;
};

const DECRYPT_PLAYBACK = ['pbkdf2', 'aes', 'restore'] as const;

export const Decrypt: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [vaultFile, setVaultFile] = useState<VaultDecryptState['vaultFile'] | null>(null);
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState<'idle' | 'decrypting' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [decryptedBlob, setDecryptedBlob] = useState<Blob | null>(null);
  const [originalFileName, setOriginalFileName] = useState('');
  const [loadingText, setLoadingText] = useState('Initializing decryption engine...');
  const [steps, setSteps] = useState<PipelineStep[]>([]);
  const playRef = useRef<number | null>(null);

  useEffect(() => {
    const incoming = (location.state as VaultDecryptState | null)?.vaultFile;
    if (!incoming) return;
    setVaultFile(incoming);
    setFile(null);
    setPassword('');
    setStatus('idle');
    setDecryptedBlob(null);
    setOriginalFileName(incoming.original_name);
    setSteps([]);
    navigate('/decrypt', { replace: true, state: {} });
  }, [location.state, navigate]);

  const stopPlayback = () => {
    if (playRef.current) {
      window.clearInterval(playRef.current);
      playRef.current = null;
    }
  };

  const clearVaultSource = () => {
    setVaultFile(null);
    setPassword('');
  };

  const handleDecrypt = async () => {
    if ((!file && !vaultFile) || !password) return;

    let pipelineSteps: PipelineStep[];
    try {
      const prep = transformPassword(password);
      const source = vaultFile
        ? `Vault · ${vaultFile.encrypted_name}`
        : file!.name;
      pipelineSteps = buildDecryptSteps(prep, source);
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(err?.message || 'Password preprocessing failed.');
      return;
    }

    setSteps(pipelineSteps);
    setStatus('decrypting');
    setProgress(8);
    setErrorMessage('');
    setDecryptedBlob(null);
    setLoadingText('Parsing ARYA header...');

    let restoredName = originalFileName;
    if (vaultFile) {
      restoredName = vaultFile.original_name;
      setOriginalFileName(vaultFile.original_name);
    } else if (file) {
      restoredName = file.name;
      if (restoredName.endsWith('.arya')) {
        restoredName = restoredName.substring(0, restoredName.length - 5);
      }
      setOriginalFileName(restoredName);
    }

    setSteps((prev) => activateStep(prev, 'parse'));

    try {
      if (file) {
        const header = await parseAryaHeader(file);
        pipelineSteps = fillDecryptHeader(pipelineSteps, header);
        setSteps(pipelineSteps);
        setProgress(28);
        setLoadingText('Header parsed. Re-deriving AES-256 key...');
      } else if (vaultFile) {
        const meta = await fileService.getContainerMeta(vaultFile.id);
        pipelineSteps = fillDecryptHeader(pipelineSteps, meta);
        setSteps(pipelineSteps);
        setProgress(28);
        setLoadingText('Vault .arya header loaded. Re-deriving AES-256 key...');
      }
    } catch {
      setLoadingText('Could not preview header locally — continuing on server...');
    }

    let playIndex = 0;
    playRef.current = window.setInterval(() => {
      const id = DECRYPT_PLAYBACK[Math.min(playIndex, DECRYPT_PLAYBACK.length - 1)];
      setSteps((prev) => activateStep(prev, id));
      setProgress((p) => Math.min(92, p + 12));
      if (id === 'pbkdf2') setLoadingText('PBKDF2 re-deriving AES-256 key (600,000 iterations)...');
      if (id === 'aes') setLoadingText('AES-GCM decrypt + auth tag verify...');
      if (id === 'restore') setLoadingText('Restoring plaintext...');
      playIndex += 1;
    }, 850);

    try {
      const { blob, pipeline } = vaultFile
        ? await fileService.decryptVaultFile(vaultFile.id, password)
        : await fileService.decryptFile(file!, password);

      stopPlayback();
      setProgress(100);
      setLoadingText('Authentication successful.');
      if (pipeline) {
        pipelineSteps = fillDecryptHeader(pipelineSteps, pipeline);
      }
      const outName = restoredName;
      setSteps(completeDecryptPipeline(pipelineSteps, outName, blob.size));
      setDecryptedBlob(blob);
      setStatus('success');
    } catch (err: any) {
      stopPlayback();
      setStatus('error');

      let message = 'Decryption failed. Please check your password.';
      if (err.response && err.response.data) {
        if (err.response.data instanceof Blob) {
          const text = await err.response.data.text();
          try {
            const json = JSON.parse(text);
            message = json.detail || message;
          } catch {
            // Ignore parse error, use default
          }
        } else if (typeof err.response.data.detail === 'string') {
          message = err.response.data.detail;
        }
      }
      setSteps((prev) => failActiveStep(prev, message));
      setErrorMessage(message);
    }
  };

  const handleDownload = () => {
    if (!decryptedBlob) return;
    const url = URL.createObjectURL(decryptedBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = originalFileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const resetState = () => {
    stopPlayback();
    setFile(null);
    setVaultFile(null);
    setPassword('');
    setStatus('idle');
    setProgress(0);
    setDecryptedBlob(null);
    setOriginalFileName('');
    setSteps([]);
  };

  const canDecrypt = Boolean((file || vaultFile) && password.length >= 8);

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto flex flex-col gap-8 pb-12">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white flex items-center justify-center gap-3">
            <Unlock className="w-8 h-8 text-emerald-400" />
            File Decryption
          </h1>
          <p className="text-slate-400 max-w-xl mx-auto">
            Unlock a vault file directly, or upload a `.arya` payload and restore with your password.
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
                {vaultFile ? (
                  <Card className="p-6 border-emerald-500/20 bg-emerald-500/5">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4 min-w-0">
                        <div className="w-12 h-12 rounded-xl bg-emerald-500/15 flex items-center justify-center shrink-0">
                          <HardDrive className="w-6 h-6 text-emerald-400" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs uppercase tracking-wider text-emerald-400/80 mb-1">From Vault</p>
                          <p className="text-lg font-semibold text-white truncate">{vaultFile.original_name}</p>
                          <p className="text-sm text-slate-400 font-mono truncate">{vaultFile.encrypted_name}</p>
                          <p className="text-xs text-slate-500 mt-2">No re-upload needed — decrypting the stored `.arya` on the server.</p>
                        </div>
                      </div>
                      <button
                        onClick={clearVaultSource}
                        className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                        title="Clear vault selection"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </Card>
                ) : (
                  <DragDropZone onFileSelect={setFile} selectedFile={file} />
                )}
              </div>
              <AnimatePresence>
                {(file || vaultFile) && (
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
                        showStrengthMeter={false}
                        label="Decryption Password"
                        placeholder="Enter the password used to lock this file..."
                      />
                    </Card>
                    <button
                      onClick={handleDecrypt}
                      disabled={!canDecrypt}
                      className="w-full py-4 rounded-xl font-bold text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg"
                    >
                      <Unlock className="w-5 h-5" />
                      {vaultFile ? 'Decrypt From Vault' : 'Decrypt Data'}
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

          {status === 'decrypting' && (
            <motion.div key="decrypting" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <PipelineVisualizer
                title="Decryption pipeline"
                subtitle={loadingText}
                steps={steps}
                progress={progress}
                accent="emerald"
                footer="parse .arya -> Aryabhata stream -> PBKDF2 -> AES-256-GCM verify -> plaintext"
              />
            </motion.div>
          )}

          {status === 'success' && (
            <motion.div
              key="success"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-6"
            >
              <Card className="p-8 w-full flex flex-col items-center text-center border-sky-500/30 bg-sky-500/5">
                <div className="w-20 h-20 rounded-full bg-sky-500/20 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(14,165,233,0.3)]">
                  <FileCheck className="w-10 h-10 text-sky-400" />
                </div>
                <h3 className="text-2xl font-bold text-sky-400 mb-2">Restoration Complete</h3>
                <p className="text-slate-300 mb-8">
                  The payload has been successfully authenticated and decrypted.
                </p>
                <div className="w-full bg-black/40 rounded-lg p-4 mb-8 text-left border border-white/5">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 text-sm">Original File</span>
                    <span className="text-slate-200 text-sm font-medium truncate max-w-[200px]">{originalFileName}</span>
                  </div>
                </div>
                <div className="w-full flex gap-4">
                  <button
                    onClick={resetState}
                    className="flex-1 py-3 px-4 rounded-lg font-medium text-slate-300 bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
                  >
                    Decrypt Another
                  </button>
                  <button
                    onClick={handleDownload}
                    className="flex-1 py-3 px-4 rounded-lg font-medium text-white bg-sky-600 hover:bg-sky-500 shadow-[0_0_15px_rgba(14,165,233,0.4)] transition-all flex items-center justify-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                </div>
              </Card>

              {steps.length > 0 && (
                <PipelineVisualizer
                  title="How this file was decrypted"
                  steps={steps}
                  progress={100}
                  accent="emerald"
                  footer="parse .arya -> Aryabhata stream -> PBKDF2 -> AES-256-GCM verify -> plaintext"
                />
              )}
            </motion.div>
          )}

          {status === 'error' && (
            <motion.div key="error" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col gap-6">
              {steps.length > 0 && (
                <PipelineVisualizer title="Decryption pipeline" steps={steps} accent="emerald" />
              )}
              <Card className="p-8 w-full flex flex-col items-center text-center border-rose-500/30 bg-rose-500/5">
                <div className="w-16 h-16 rounded-full bg-rose-500/20 flex items-center justify-center mb-6">
                  <AlertTriangle className="w-8 h-8 text-rose-400" />
                </div>
                <h3 className="text-xl font-bold text-rose-400 mb-2">Decryption Failed</h3>
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
