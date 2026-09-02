import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { User, Lock, SlidersHorizontal, Loader2, CheckCircle2, Info } from 'lucide-react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import {
  authService,
  changePasswordSchema,
  updateEmailSchema,
  loadPrefs,
  savePrefs,
  type ChangePasswordData,
  type UpdateEmailData,
  type UserProfile,
  type UserPrefs,
} from '@/services/auth.service';
import { BRAND, PRODUCT_NAME, PRODUCT_TAGLINE } from '@/brand/constants';

export function Settings() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [prefs, setPrefs] = useState<UserPrefs>(loadPrefs);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [emailMsg, setEmailMsg] = useState('');
  const [emailErr, setEmailErr] = useState('');
  const [pwdMsg, setPwdMsg] = useState('');
  const [pwdErr, setPwdErr] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [pwdLoading, setPwdLoading] = useState(false);

  const emailForm = useForm<UpdateEmailData>({
    resolver: zodResolver(updateEmailSchema),
    defaultValues: { email: '' },
  });

  const passwordForm = useForm<ChangePasswordData>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
  });

  useEffect(() => {
    const load = async () => {
      try {
        const me = await authService.me();
        setProfile(me);
        emailForm.reset({ email: me.email });
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingProfile(false);
      }
    };
    load();
  }, [emailForm]);

  const onUpdateEmail = async (data: UpdateEmailData) => {
    try {
      setEmailLoading(true);
      setEmailErr('');
      setEmailMsg('');
      const updated = await authService.updateEmail(data);
      setProfile(updated);
      setEmailMsg('Email updated successfully.');
      window.dispatchEvent(new Event('aryacrypt-profile-updated'));
    } catch (err: any) {
      setEmailErr(err.response?.data?.detail || 'Failed to update email.');
    } finally {
      setEmailLoading(false);
    }
  };

  const onChangePassword = async (data: ChangePasswordData) => {
    try {
      setPwdLoading(true);
      setPwdErr('');
      setPwdMsg('');
      await authService.changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
      });
      passwordForm.reset();
      setPwdMsg('Password changed. Please sign in again.');
      window.setTimeout(() => {
        window.location.href = '/login';
      }, 800);
    } catch (err: any) {
      setPwdErr(err.response?.data?.detail || 'Failed to change password.');
    } finally {
      setPwdLoading(false);
    }
  };

  const togglePref = (key: keyof UserPrefs) => {
    const next = { ...prefs, [key]: !prefs[key] };
    setPrefs(next);
    savePrefs(next);
  };

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto flex flex-col gap-8">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Account Settings</h2>
          <p className="text-slate-400 mt-1">Manage your profile, password, and vault preferences.</p>
        </div>

        {/* Profile */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <User className="w-5 h-5 text-sky-400" />
              <h3 className="text-lg font-semibold text-slate-100">Profile</h3>
            </div>

            {loadingProfile ? (
              <div className="flex items-center gap-2 text-slate-400 py-6">
                <Loader2 className="w-5 h-5 animate-spin" />
                Loading profile...
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6 text-sm">
                  <div className="rounded-lg bg-white/5 border border-white/10 p-4">
                    <p className="text-slate-500 mb-1">User ID</p>
                    <p className="text-slate-200 font-mono text-xs break-all">{profile?.id}</p>
                  </div>
                  <div className="rounded-lg bg-white/5 border border-white/10 p-4">
                    <p className="text-slate-500 mb-1">Member since</p>
                    <p className="text-slate-200">
                      {profile?.created_at
                        ? new Date(profile.created_at).toLocaleDateString(undefined, {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })
                        : '—'}
                    </p>
                  </div>
                </div>

                <Form {...emailForm}>
                  <form onSubmit={emailForm.handleSubmit(onUpdateEmail)} className="space-y-4">
                    <FormField
                      control={emailForm.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input {...field} className="bg-background/50" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    {emailErr && <p className="text-sm text-rose-400">{emailErr}</p>}
                    {emailMsg && (
                      <p className="text-sm text-emerald-400 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4" /> {emailMsg}
                      </p>
                    )}
                    <Button type="submit" disabled={emailLoading}>
                      {emailLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                      Save email
                    </Button>
                  </form>
                </Form>
              </>
            )}
          </Card>
        </motion.div>

        {/* Password */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Lock className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-slate-100">Change Password</h3>
            </div>
            <Form {...passwordForm}>
              <form onSubmit={passwordForm.handleSubmit(onChangePassword)} className="space-y-4">
                <FormField
                  control={passwordForm.control}
                  name="current_password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Current password</FormLabel>
                      <FormControl>
                        <Input type="password" {...field} className="bg-background/50" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={passwordForm.control}
                  name="new_password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>New password</FormLabel>
                      <FormControl>
                        <Input type="password" {...field} className="bg-background/50" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={passwordForm.control}
                  name="confirm_password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirm new password</FormLabel>
                      <FormControl>
                        <Input type="password" {...field} className="bg-background/50" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                {pwdErr && <p className="text-sm text-rose-400">{pwdErr}</p>}
                {pwdMsg && (
                  <p className="text-sm text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" /> {pwdMsg}
                  </p>
                )}
                <Button type="submit" disabled={pwdLoading}>
                  {pwdLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  Update password
                </Button>
              </form>
            </Form>
          </Card>
        </motion.div>

        {/* Preferences */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <SlidersHorizontal className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-semibold text-slate-100">Preferences</h3>
            </div>
            <div className="space-y-4">
              <label className="flex items-center justify-between gap-4 rounded-lg border border-white/10 bg-white/5 px-4 py-3 cursor-pointer">
                <div>
                  <p className="text-slate-200 font-medium">Compact activity list</p>
                  <p className="text-sm text-slate-500">Show denser rows on the dashboard history table.</p>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.compactActivity}
                  onChange={() => togglePref('compactActivity')}
                  className="h-4 w-4 accent-sky-500"
                />
              </label>
              <label className="flex items-center justify-between gap-4 rounded-lg border border-white/10 bg-white/5 px-4 py-3 cursor-pointer">
                <div>
                  <p className="text-slate-200 font-medium">Security alert reminders</p>
                  <p className="text-sm text-slate-500">Highlight failed decrypt attempts in the dashboard.</p>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.emailAlerts}
                  onChange={() => togglePref('emailAlerts')}
                  className="h-4 w-4 accent-sky-500"
                />
              </label>
            </div>
          </Card>
        </motion.div>

        {/* About */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Info className="w-5 h-5 text-sky-400" />
              <h3 className="text-lg font-semibold text-slate-100">About</h3>
            </div>
            <div className="space-y-3 text-sm">
              <p className="text-xl font-bold tracking-tight text-slate-100">{PRODUCT_NAME}</p>
              <p className="text-slate-400">{PRODUCT_TAGLINE}</p>
              <div className="pt-3 border-t border-white/10 flex flex-col gap-1">
                <p className="text-slate-500">
                  Framework version:{' '}
                  <span className="font-mono text-slate-300">{BRAND.version}</span>
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}
