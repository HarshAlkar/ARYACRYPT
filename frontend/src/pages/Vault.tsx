import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Filter, Trash2, HardDrive, FileKey2, ChevronLeft, ChevronRight, Loader2, ShieldCheck, Download, Unlock } from 'lucide-react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '../components/ui/Card';
import { fileService, type FileResponseDTO } from '../services/file.service';

export const Vault: React.FC = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<FileResponseDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest' | 'largest' | 'smallest'>('newest');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      setIsLoading(true);
      const data = await fileService.getHistory();
      setFiles(data);
    } catch (error) {
      console.error("Failed to fetch history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to permanently delete this file? This action cannot be undone.")) return;
    try {
      await fileService.deleteFile(id);
      setFiles(files.filter(f => f.id !== id));
    } catch (error) {
      console.error("Failed to delete file:", error);
      alert("Failed to delete the file.");
    }
  };

  const handleDownload = async (file: FileResponseDTO) => {
    try {
      await fileService.downloadEncryptedFile(file.id, file.encrypted_name);
    } catch (error) {
      console.error("Failed to download file:", error);
      alert("Failed to download the encrypted file.");
    }
  };

  const handleOpenInDecrypt = (file: FileResponseDTO) => {
    navigate('/decrypt', {
      state: {
        vaultFile: {
          id: file.id,
          original_name: file.original_name,
          encrypted_name: file.encrypted_name,
        },
      },
    });
  };

  const filteredAndSortedFiles = useMemo(() => {
    let result = [...files];
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(f => 
        f.original_name.toLowerCase().includes(q) || 
        f.encrypted_name.toLowerCase().includes(q) ||
        f.id.toLowerCase().includes(q)
      );
    }
    switch (sortOrder) {
      case 'newest':
        result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        break;
      case 'oldest':
        result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        break;
      case 'largest':
        result.sort((a, b) => b.file_size_bytes - a.file_size_bytes);
        break;
      case 'smallest':
        result.sort((a, b) => a.file_size_bytes - b.file_size_bytes);
        break;
    }
    return result;
  }, [files, searchQuery, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(filteredAndSortedFiles.length / itemsPerPage));
  const currentData = filteredAndSortedFiles.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  useEffect(() => {
    if (currentPage > totalPages) setCurrentPage(1);
  }, [totalPages, currentPage]);

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto flex flex-col gap-6 h-full min-h-[calc(100vh-8rem)]">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-2">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <HardDrive className="w-8 h-8 text-sky-400" />
              My Vault
            </h1>
            <p className="text-slate-400 mt-1">Manage, download, or decrypt your encrypted payload history.</p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text"
                placeholder="Search files or UUID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-black/20 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 transition-all"
              />
            </div>
            <div className="relative group w-full sm:w-auto">
              <select 
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value as any)}
                className="w-full sm:w-auto appearance-none bg-black/20 border border-white/10 rounded-lg pl-10 pr-10 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 transition-all cursor-pointer"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="largest">Largest Files</option>
                <option value="smallest">Smallest Files</option>
              </select>
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>
        </div>

        <Card className="flex-1 flex flex-col overflow-hidden border-white/5 h-full">
          <div className="overflow-x-auto flex-1 h-[500px]">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead className="bg-black/40 sticky top-0 z-10 backdrop-blur-md shadow-sm">
                <tr className="text-slate-400 text-xs uppercase tracking-wider">
                  <th className="p-4 font-medium rounded-tl-xl">File Name</th>
                  <th className="p-4 font-medium">Encryption Date</th>
                  <th className="p-4 font-medium">Algorithm</th>
                  <th className="p-4 font-medium">Framework</th>
                  <th className="p-4 font-medium">Status</th>
                  <th className="p-4 font-medium text-right rounded-tr-xl">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {isLoading ? (
                  <tr>
                    <td colSpan={6} className="p-16 text-center text-slate-500">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3 text-sky-400" />
                      Loading vault history...
                    </td>
                  </tr>
                ) : currentData.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-16 text-center text-slate-500">
                      <FileKey2 className="w-12 h-12 mx-auto mb-3 opacity-20" />
                      {searchQuery ? "No files match your search criteria." : "Your vault is currently empty."}
                    </td>
                  </tr>
                ) : (
                  currentData.map((file) => (
                    <motion.tr 
                      key={file.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      whileHover={{ backgroundColor: 'rgba(255,255,255,0.02)' }}
                      className="group transition-colors"
                    >
                      <td className="p-4">
                        <div className="flex flex-col">
                          <span className="font-medium text-slate-200 group-hover:text-sky-400 transition-colors truncate max-w-[200px]" title={file.original_name}>
                            {file.original_name}
                          </span>
                          <span className="text-xs text-slate-500 font-mono truncate max-w-[200px]" title={file.encrypted_name}>
                            {file.encrypted_name}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex flex-col">
                          <span className="text-slate-300 text-sm">
                            {new Date(file.created_at).toLocaleDateString()}
                          </span>
                          <span className="text-xs text-slate-500">
                            {new Date(file.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className="text-xs font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/5">
                          AES-256-GCM
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-xs text-slate-400 font-medium">Aryabhata v1.1</span>
                      </td>
                      <td className="p-4">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <ShieldCheck className="w-3.5 h-3.5" /> Secured
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <div className="inline-flex items-center gap-1 opacity-0 group-hover:opacity-100 focus-within:opacity-100">
                          <button 
                            onClick={() => handleOpenInDecrypt(file)}
                            className="p-2 text-slate-500 hover:text-sky-400 hover:bg-sky-500/10 rounded-lg transition-colors"
                            title="Decrypt from vault"
                          >
                            <Unlock className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => handleDownload(file)}
                            className="p-2 text-slate-500 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors"
                            title="Download .arya"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => handleDelete(file.id)}
                            className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                            title="Permanently Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {!isLoading && filteredAndSortedFiles.length > 0 && (
            <div className="flex items-center justify-between p-4 border-t border-white/5 bg-black/20">
              <span className="text-sm text-slate-400">
                Showing <span className="text-slate-200">{((currentPage - 1) * itemsPerPage) + 1}</span> to <span className="text-slate-200">{Math.min(currentPage * itemsPerPage, filteredAndSortedFiles.length)}</span> of <span className="text-slate-200">{filteredAndSortedFiles.length}</span> files
              </span>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-1.5 rounded-md bg-white/5 text-slate-300 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="text-sm font-medium text-slate-200 min-w-[3rem] text-center">
                  {currentPage} / {totalPages}
                </span>
                <button 
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-1.5 rounded-md bg-white/5 text-slate-300 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </DashboardLayout>
  );
};
