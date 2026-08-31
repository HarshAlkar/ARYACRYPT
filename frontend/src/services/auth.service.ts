import { api, refreshAccessToken } from './api';
import { clearAccessToken, getAccessToken, setAccessToken } from './tokenStore';
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

export const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

export const changePasswordSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: z.string().min(6, "New password must be at least 6 characters"),
  confirm_password: z.string().min(1, "Please confirm your password"),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

export const updateEmailSchema = z.object({
  email: z.string().email("Invalid email address"),
});

export type LoginData = z.infer<typeof loginSchema>;
export type RegisterData = z.infer<typeof registerSchema>;
export type ChangePasswordData = z.infer<typeof changePasswordSchema>;
export type UpdateEmailData = z.infer<typeof updateEmailSchema>;

export interface UserProfile {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export const PREFS_KEY = 'aryacrypt_prefs';

export interface UserPrefs {
  compactActivity: boolean;
  emailAlerts: boolean;
}

export const defaultPrefs: UserPrefs = {
  compactActivity: false,
  emailAlerts: true,
};

export function loadPrefs(): UserPrefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    if (!raw) return { ...defaultPrefs };
    return { ...defaultPrefs, ...JSON.parse(raw) };
  } catch {
    return { ...defaultPrefs };
  }
}

export function savePrefs(prefs: UserPrefs): void {
  localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
}

export const authService = {
  login: async (data: LoginData) => {
    const response = await api.post('/auth/login', data);
    if (response.data.access_token) {
      // Access token: memory only. Refresh: HttpOnly cookie from Set-Cookie.
      setAccessToken(response.data.access_token);
    }
    return response.data;
  },

  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  me: async (): Promise<UserProfile> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  updateEmail: async (data: UpdateEmailData): Promise<UserProfile> => {
    const response = await api.patch('/auth/me', data);
    return response.data;
  },

  changePassword: async (data: { current_password: string; new_password: string }) => {
    const response = await api.post('/auth/change-password', data);
    // Password change bumps token_version; drop access token — user must re-login
    clearAccessToken();
    return response.data;
  },

  refresh: async () => {
    const access = await refreshAccessToken();
    if (!access) throw new Error('No refresh session');
    return { access_token: access };
  },

  /** Restore access token from HttpOnly refresh cookie after reload. */
  bootstrapSession: async (): Promise<boolean> => {
    if (getAccessToken()) return true;
    const access = await refreshAccessToken();
    return Boolean(access);
  },

  logout: async () => {
    try {
      await api.post('/auth/logout', {});
    } catch {
      // Still clear local session even if server logout fails
    }
    clearAccessToken();
  },

  isAuthenticated: () => Boolean(getAccessToken()),
};
