import { api } from './api';

export interface FileResponseDTO {
  id: string;
  original_name: string;
  encrypted_name: string;
  file_size_bytes: number;
  created_at: string;
}

export interface ActivityItem {
  id: string;
  action: string;
  status: string;
  original_name: string | null;
  file_size_bytes: number | null;
  duration_ms: number | null;
  created_at: string;
}

export interface VaultStats {
  total_files: number;
  total_encrypted: number;
  total_decrypted: number;
  security_alerts: number;
  storage_used_bytes: number;
  storage_capacity_bytes: number;
  trends: { files: number; encrypt: number; decrypt: number };
  recent_activity: ActivityItem[];
  daily_volume: { date: string; size_mb: number; count: number }[];
  daily_ops: {
    date: string;
    size_mb: number;
    count: number;
    encrypt_count: number;
    decrypt_count: number;
  }[];
  processing: { size_mb: number; time_ms: number; action: string }[];
  success_rate: { success: number; failure: number };
}

export const fileService = {
  getHistory: async (): Promise<FileResponseDTO[]> => {
    const response = await api.get('/files/history');
    return response.data;
  },

  getStats: async (): Promise<VaultStats> => {
    const response = await api.get('/files/stats');
    return response.data;
  },

  encryptFile: async (file: File, password: string): Promise<FileResponseDTO> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    const response = await api.post('/files/encrypt', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  decryptFile: async (file: File, password: string): Promise<Blob> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    const response = await api.post('/files/decrypt', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    });
    return response.data;
  },

  deleteFile: async (id: string): Promise<void> => {
    await api.delete(`/files/${id}`);
  },

  decryptVaultFile: async (id: string, password: string): Promise<Blob> => {
    const formData = new FormData();
    formData.append('password', password);

    const response = await api.post(`/files/${id}/decrypt`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    });
    return response.data;
  },

  downloadEncryptedFile: async (id: string, filename: string): Promise<void> => {
    const response = await api.get(`/files/${id}/download`, {
      responseType: 'blob',
    });

    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename.endsWith('.arya') ? filename : `${filename}.arya`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  },
};
