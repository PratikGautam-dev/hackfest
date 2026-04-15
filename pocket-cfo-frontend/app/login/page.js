'use client';

import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { DM_Sans, Syne } from 'next/font/google';
import { AlertCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-body', weight: ['400', '500', '700'] });
const syne = Syne({ subsets: ['latin'], variable: '--font-heading', weight: ['400', '600', '700', '800'] });

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    // Natively invoke secure credentials bounded session matrix implicitly
    const res = await signIn("credentials", { email, password, redirect: false });
    
    if (res?.error) {
      setError("Invalid credentials structurally mapped. Check your password.");
      setLoading(false);
    } else {
      router.push("/dashboard");
    }
  };

  const loadDemo = () => {
    setEmail("demo@pocketcfo.in");
    setPassword("demo123");
  };

  return (
    <div className={`min-h-screen bg-[#0D0F12] text-slate-200 flex ${dmSans.variable} ${syne.variable} font-body bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]`}>
      
      {/* Brand Panel (Left) */}
      <div className="hidden lg:flex flex-col flex-1 border-r border-slate-800 bg-[#111318] p-16 justify-center relative overflow-hidden">
        {/* Glow effect safely bounding ambient styling natively */}
        <div className="absolute top-1/4 -right-32 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl shadow-2xl"></div>
        
        <div className="z-10 max-w-md">
          <div className="flex items-center gap-3 text-amber-500 font-heading font-bold text-4xl mb-6">
            <span className="bg-amber-500 text-[#111318] w-12 h-12 flex items-center justify-center rounded-xl">₹</span>
            <span className="text-white">Pocket CFO</span>
          </div>
          
          <h1 className="font-heading text-4xl font-bold text-slate-100 leading-tight mb-4">
            Your AI-powered CA for Indian SMBs
          </h1>
          <p className="text-lg text-slate-400 mb-12">
            Automate your bookkeeping, detect tax recovery opportunities, and decode real-time financial health using AI.
          </p>
          
          <ul className="space-y-6 text-slate-300 font-medium">
            {[
              "Automatic SMS & PDF parsing seamlessly extracting structural logic",
              "GST ITC detection intrinsically bound across operational parameters",
              "Real-time profit intelligence evaluating margins safely natively"
            ].map((text, i) => (
              <li key={i} className="flex items-center gap-4 border border-slate-800 rounded-xl p-4 bg-slate-900/50">
                <div className="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
                {text}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Auth Form Panel (Right) */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 bg-[#0D0F12]">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 text-amber-500 font-heading font-bold text-3xl mb-12 justify-center">
            <span className="bg-amber-500 text-[#111318] w-10 h-10 flex items-center justify-center rounded-xl">₹</span>
            <span className="text-white">Pocket CFO</span>
          </div>
          
          <h2 className="text-2xl font-heading font-bold text-slate-100 mb-2 whitespace-nowrap">Welcome Back</h2>
          <p className="text-sm text-slate-500 mb-8 font-medium">Please enter your credentials to access your dashboard.</p>
          
          <form onSubmit={handleLogin} className="space-y-5">
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Email Address</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-3 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-colors"
                placeholder="you@company.com"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Password</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-[#111318] border border-slate-800 rounded-lg px-4 py-3 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-colors"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-950/30 border border-red-500/30 rounded-lg flex items-center gap-2 text-sm text-red-400 font-medium">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold py-3.5 rounded-lg transition-transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 mt-4"
            >
              {loading ? "Authenticating..." : (
                <>Sign In Securely <ArrowRight size={18} strokeWidth={2.5} /></>
              )}
            </button>
          </form>

          <div className="mt-8 flex flex-col space-y-4">
            <button 
              type="button"
              onClick={loadDemo}
              className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-medium py-3 rounded-lg transition-colors text-sm"
            >
              Try Demo Credentials Automatically
            </button>
            
            <div className="text-center text-sm font-medium text-slate-500 mt-6">
              Don't have an account? <Link href="/register" className="text-amber-500 hover:text-amber-400 transition-colors ml-1">Sign up</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
