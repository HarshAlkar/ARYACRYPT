import { api } from './api';

export interface FileResponseDTO {
  id: string;
  original_name: string;
  encrypted_name: string;
  file_size_bytes: number;
  created_at: string;
}

export const fileService = {
  getHistory: async (): Promise<FileResponseDTO[]> => {
    const response = await api.get('/files/history');
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
      responseType: 'blob', // crucial for receiving the binary file
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
