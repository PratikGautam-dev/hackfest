'use client';

import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { DM_Sans, Syne } from 'next/font/google';
import { AlertCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-body', weight: ['400', '500', '700'] });
const syne = Syne({ subsets: ['latin'], variable: '--font-heading', weight: ['400', '600', '700', '800'] });

export default function Register() {
  const router = useRouter();
  
  const [formData, setFormData] = useState({
    name: '',
    businessName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: ''
  });
  
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    // Strict client validation schema securely
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match computationally.");
      setLoading(false);
      return;
    }
    
    if (formData.password.length < 6) {
      setError("Complexity constraint bypassed natively. Ensure at least 6 characters.");
      setLoading(false);
      return;
    }

    try {
      // Direct REST evaluation mapping limits explicitly natively internally
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          businessName: formData.businessName,
          phone: formData.phone,
          password: formData.password
        })
      });

      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || "Execution binding failed securely");
      }
      
      // Inherently securely hook authentication seamlessly following registration natively implicitly
      const authRes = await signIn("credentials", { 
        email: formData.email, 
        password: formData.password, 
        redirect: false 
      });
      
      if (authRes?.error) {
        throw new Error("Account spawned natively but login validation bypassed.");
      }
      
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className={`min-h-screen bg-[#0D0F12] text-slate-200 flex ${dmSans.variable} ${syne.variable} font-body bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]`}>
      
      {/* Brand Panel (Left) */}
      <div className="hidden lg:flex flex-col flex-1 border-r border-slate-800 bg-[#111318] p-16 justify-center relative overflow-hidden">
        {/* Glow bounds natively mapped structurally centrally isolated*/}
        <div className="absolute bottom-1/4 -left-32 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl shadow-2xl"></div>
        
        <div className="z-10 max-w-md ml-auto mr-12">
          <div className="flex items-center gap-3 text-amber-500 font-heading font-bold text-4xl mb-6">
            <span className="bg-amber-500 text-[#111318] w-12 h-12 flex items-center justify-center rounded-xl">₹</span>
            <span className="text-white">Pocket CFO</span>
          </div>
          
          <h1 className="font-heading text-4xl font-bold text-slate-100 leading-tight mb-4">
            Initialize Command Center
          </h1>
          <p className="text-lg text-slate-400 mb-12">
             Sign up securely today mapping analytical AI safely natively into your unstructured financial ledgers seamlessly.
          </p>
        </div>
      </div>

      {/* Auth Form Panel (Right) */}
      <div className="flex-[1.2] flex flex-col justify-center items-center p-8 bg-[#0D0F12] py-16">
        <div className="w-full max-w-lg">
          <div className="lg:hidden flex items-center gap-3 text-amber-500 font-heading font-bold text-3xl mb-12 justify-center">
            <span className="bg-amber-500 text-[#111318] w-10 h-10 flex items-center justify-center rounded-xl">₹</span>
            <span className="text-white">Pocket CFO</span>
          </div>
          
          <h2 className="text-2xl font-heading font-bold text-slate-100 mb-2">Create Account</h2>
          <p className="text-sm text-slate-500 mb-8 font-medium">Establish a secure bounds explicit pipeline directly isolating local logic natively.</p>
          
          <form onSubmit={handleRegister} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Full Name</label>
                <input 
                  type="text" 
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Business Name</label>
                <input 
                  type="text" 
                  name="businessName"
                  value={formData.businessName}
                  onChange={handleChange}
                  required
                  className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Email Address</label>
                <input 
                  type="email" 
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Phone (Optional)</label>
                <input 
                  type="text" 
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Password</label>
                <input 
                  type="password" 
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Confirm Password</label>
                <input 
                  type="password" 
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                />
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-950/30 border border-red-500/30 rounded-lg flex items-center gap-2 text-sm text-red-400 font-medium mt-4">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold py-3.5 rounded-lg transition-transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 mt-6"
            >
              {loading ? "Constructing Limits..." : (
                <>Establish Account Natively <ArrowRight size={18} strokeWidth={2.5} /></>
              )}
            </button>
          </form>

          <div className="mt-8 text-center text-sm font-medium text-slate-500 flex flex-col space-y-4">
            <div>
              Already have an account? <Link href="/login" className="text-amber-500 hover:text-amber-400 transition-colors ml-1">Login directly</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
