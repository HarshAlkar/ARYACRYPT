import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud, File as FileIcon, X, CheckCircle2 } from 'lucide-react';
import { Card } from './Card';

interface DragDropZoneProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export const DragDropZone: React.FC<DragDropZoneProps> = ({ onFileSelect, selectedFile }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFileSelect(null);
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="p-1 relative overflow-hidden h-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !selectedFile && document.getElementById('file-upload')?.click()}
        className={`relative w-full h-full min-h-[280px] border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 transition-all duration-300 ${
          isDragging 
            ? 'border-sky-400 bg-sky-500/10' 
            : selectedFile 
              ? 'border-emerald-500/30 bg-emerald-500/5 cursor-default'
              : 'border-white/10 hover:border-sky-500/30 hover:bg-white/5 cursor-pointer'
        }`}
      >
        <input 
          id="file-upload" 
          type="file" 
          className="hidden" 
          onChange={handleFileInput}
        />

        {!selectedFile ? (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center gap-5 text-center pointer-events-none"
          >
            <motion.div 
              animate={{ y: [0, -10, 0] }} 
              transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
              className="p-5 rounded-full bg-sky-500/10 shadow-[0_0_20px_rgba(14,165,233,0.2)]"
            >
              <UploadCloud className="w-12 h-12 text-sky-400" />
            </motion.div>
            <div>
              <h3 className="text-xl font-semibold text-slate-100">Drag & Drop file to secure</h3>
              <p className="text-sm text-slate-400 mt-2">or click anywhere to browse local files</p>
            </div>
            <div className="flex flex-wrap justify-center gap-2 mt-2">
              {['PDF', 'PNG', 'JPG', 'DOCX', 'XLSX', 'ZIP'].map(ext => (
                <span key={ext} className="text-xs px-2.5 py-1 rounded-md bg-white/5 text-slate-400 border border-white/5">
                  {ext}
                </span>
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full flex items-center justify-between bg-white/5 p-5 rounded-xl border border-white/10"
          >
            <div className="flex items-center gap-4">
              <div className="p-4 bg-emerald-500/20 rounded-xl shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                <FileIcon className="w-8 h-8 text-emerald-400" />
              </div>
              <div className="flex flex-col gap-1">
                <h4 className="font-semibold text-slate-100 truncate max-w-[200px] md:max-w-[400px]">
                  {selectedFile.name}
                </h4>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <span>{formatSize(selectedFile.size)}</span>
                  <span className="w-1 h-1 rounded-full bg-slate-600" />
                  <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" /> File Ready
                  </span>
                </div>
              </div>
            </div>
            <button 
              onClick={clearFile}
              className="p-2 hover:bg-rose-500/20 hover:text-rose-400 rounded-lg transition-colors text-slate-400"
              title="Remove File"
            >
              <X className="w-5 h-5" />
            </button>
          </motion.div>
        )}
      </div>
    </Card>
  );
};
