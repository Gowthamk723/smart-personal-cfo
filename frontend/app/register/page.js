"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import Link from 'next/link';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await authAPI.register({ email, password });
      setSuccess(true);
      setTimeout(() => router.push('/'), 2000); 
    } catch (err) {
      alert("Registration failed: " + (err.response?.data?.detail || "Error"));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 border border-slate-100">
        <h2 className="text-3xl font-bold text-slate-900 mb-2">Create Account</h2>
        <p className="text-slate-500 mb-8">Join the Smart CFO community.</p>

        {success ? (
          <div className="bg-emerald-50 text-emerald-600 p-4 rounded-xl font-medium">
            Success! Redirecting to login...
          </div>
        ) : (
          <form onSubmit={handleRegister} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Email</label>
              <input 
                type="email" 
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500/20 outline-none"
                onChange={(e) => setEmail(e.target.value)}
                required 
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Password</label>
              <input 
                type="password" 
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500/20 outline-none"
                onChange={(e) => setPassword(e.target.value)}
                required 
              />
            </div>
            <button className="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-blue-700 transition-all">
              Sign Up
            </button>
            <p className="text-center text-sm text-slate-500">
              Already have an account? <Link href="/" className="text-blue-600 font-bold underline">Login</Link>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}