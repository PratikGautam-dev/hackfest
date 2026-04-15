'use client';

import { LayoutDashboard, LineChart, FileText, User, LogOut } from 'lucide-react';
import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const { data: session } = useSession();
  const pathname = usePathname();
  
  return (
    <aside className="w-[240px] fixed inset-y-0 left-0 bg-[#111318] border-r border-slate-800 flex flex-col z-20">
      <div className="p-6">
        <div className="flex items-center gap-3 text-amber-500 font-heading font-bold text-2xl tracking-tight">
          <span className="bg-amber-500 text-[#111318] w-8 h-8 flex items-center justify-center rounded-lg text-lg">₹</span>
          <span className="text-white">Pocket CFO</span>
        </div>
        <p className="text-xs text-slate-500 mt-2 font-medium uppercase tracking-wider">Command Center</p>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        <Link 
          href="/dashboard" 
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors ${
            pathname === '/dashboard' 
              ? 'bg-amber-500/10 text-amber-500' 
              : 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          <LayoutDashboard size={18} /> Dashboard
        </Link>
        <Link 
          href="/dashboard/insights" 
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors ${
            pathname === '/dashboard/insights' 
              ? 'bg-amber-500/10 text-amber-500' 
              : 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          <LineChart size={18} /> Insights
        </Link>
        <Link 
          href="/dashboard/transactions" 
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors ${
            pathname === '/dashboard/transactions' 
              ? 'bg-amber-500/10 text-amber-500' 
              : 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText size={18} /> Transactions
        </Link>
      </nav>
      
      <div className="p-4 border-t border-slate-800 mb-6 mx-4 rounded-xl bg-slate-900 shadow-inner">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-amber-500/20 text-amber-500 flex items-center justify-center font-bold">
            <User size={18} />
          </div>
          <div className="flex-1 overflow-hidden">
            <h4 className="text-sm font-semibold text-white truncate">{session?.user?.name || 'Loading...'}</h4>
            <p className="text-xs text-slate-500 truncate">{session?.user?.businessName || 'Synchronizing...'}</p>
          </div>
        </div>
        
        <button 
          onClick={() => signOut({ callbackUrl: '/login' })}
          className="w-full flex items-center gap-2 justify-center py-2.5 bg-red-950/30 border border-red-900/50 text-red-400 hover:bg-red-900/50 hover:text-red-300 rounded-lg text-sm font-bold transition-colors"
        >
          <LogOut size={16} strokeWidth={2.5} /> Log Out
        </button>
      </div>
    </aside>
  );
}
