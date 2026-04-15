'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { DM_Sans, Syne } from 'next/font/google';
import Sidebar from '@/components/Sidebar';
import { RefreshCw, LayoutTemplate, PieChart, ShieldCheck } from 'lucide-react';

const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-body', weight: ['400', '500', '700'] });
const syne = Syne({ subsets: ['latin'], variable: '--font-heading', weight: ['400', '600', '700', '800'] });

const formatCurrency = (amount) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);

export default function InsightsPage() {
  const { data: session, status } = useSession();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const USER_ID = session?.user?.backend_user_id;

  useEffect(() => {
    if (status === "authenticated" && USER_ID) {
      fetchInsights();
    }
  }, [status, USER_ID]);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/insights/${USER_ID}`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Failed executing insight dependencies natively:", err);
    } finally {
      setLoading(false);
    }
  };

  if (status === "loading" || !USER_ID) {
    return <div className="min-h-screen bg-[#0D0F12] flex items-center justify-center"><RefreshCw className="animate-spin text-amber-500" size={32}/></div>;
  }

  const expenseCategories = data?.expense_summary?.by_category || {};
  const maxExpense = Math.max(...Object.values(expenseCategories).map(c => c.total_amount), 1);
  const itcOps = data?.profit_summary?.itc_opportunities || [];

  return (
    <div className={`min-h-screen bg-[#0D0F12] text-slate-200 flex ${dmSans.variable} ${syne.variable} font-body bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]`}>
      <Sidebar />
      <main className="flex-1 ml-[240px] p-8 pb-32">
        
        <div className="flex items-center justify-between mb-8">
            <h1 className="font-heading text-3xl font-bold text-white">Financial Intelligence</h1>
            <button 
                onClick={fetchInsights}
                className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-amber-500 transition-colors shadow-sm"
            >
                <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
            </button>
        </div>

        {loading ? (
          <div className="flex flex-col h-64 items-center justify-center text-slate-500">
             <RefreshCw className="animate-spin text-amber-500 mb-4" size={32} /> 
             <p className="font-medium text-slate-400">Compiling multi-agent algorithmic structures...</p>
          </div>
        ) : (
          <div className="space-y-10">
            
            {/* Profit Summary */}
            <section>
              <h2 className="text-xl font-heading font-bold text-slate-200 mb-5 inline-flex items-center gap-2">
                <LayoutTemplate size={18} className="text-amber-500"/> Operational Yield Summary
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                {[
                  { label: "Total Revenue Streams", val: data?.profit_summary?.total_revenue, isProfit: true },
                  { label: "Aggregate Expenditures", val: data?.profit_summary?.total_expenses, isProfit: false },
                  { label: "Gross Target Profit", val: data?.profit_summary?.gross_profit, isProfit: data?.profit_summary?.gross_profit >= 0 },
                  { label: "Net Yield (Incl. ITC)", val: data?.profit_summary?.net_profit, isProfit: data?.profit_summary?.net_profit >= 0 }
                ].map((s, i) => (
                  <div key={i} className="bg-[#111318] p-6 rounded-xl border border-slate-800 shadow-sm relative overflow-hidden group hover:border-slate-700 transition-colors">
                    <div className={`absolute -top-10 -right-10 w-24 h-24 blur-2xl rounded-bl-full transition-colors ${s.isProfit ? 'bg-emerald-500/20 group-hover:bg-emerald-500/30' : 'bg-rose-500/20 group-hover:bg-rose-500/30'}`}></div>
                    <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">{s.label}</p>
                    <p className={`font-heading text-[28px] font-bold mt-2 ${s.isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {formatCurrency(s.val)}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* Expense Breakdown */}
            <section>
               <h2 className="text-xl font-heading font-bold text-slate-200 mb-5 inline-flex items-center gap-2">
                <PieChart size={18} className="text-amber-500"/> Spending Categorization
              </h2>
              <div className="bg-[#111318] rounded-xl border border-slate-800 p-8 space-y-6 shadow-sm">
                {Object.entries(expenseCategories).sort((a,b) => b[1].total_amount - a[1].total_amount).map(([cat, info], i) => {
                  const percent = (info.total_amount / maxExpense) * 100;
                  return (
                    <div key={i} className="space-y-2 group">
                      <div className="flex justify-between items-end text-sm">
                        <span className="font-bold text-slate-300 group-hover:text-amber-500 transition-colors">{cat} <span className="text-slate-600 font-mono text-[11px] ml-2 tracking-wider">[{info.count} TXNS]</span></span>
                        <span className="font-heading font-bold text-[16px] text-slate-200">{formatCurrency(info.total_amount)}</span>
                      </div>
                      <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden shadow-inner">
                        <div className="bg-gradient-to-r from-amber-600 to-amber-400 h-full rounded-full transition-all duration-1000 ease-out relative" style={{ width: `${Math.max(percent, 2)}%` }}>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* ITC Opportunities */}
            <section>
              <h2 className="text-xl font-heading font-bold text-slate-200 mb-5 inline-flex items-center gap-2">
                <ShieldCheck size={18} className="text-emerald-500"/> Recoverable Tax Intelligence (ITC)
              </h2>
              <div className="bg-[#111318] rounded-xl border border-slate-800 overflow-hidden shadow-sm">
                <table className="w-full text-left border-collapse">
                  <thead>
                     <tr className="bg-slate-900 text-slate-400 text-[11px] font-bold uppercase tracking-widest border-b border-slate-800">
                       <th className="p-5">Eligible B2B Target</th>
                       <th className="p-5">Gross Parameter</th>
                       <th className="p-5 text-center">Assessed Tax Class</th>
                       <th className="p-5 text-right">Yield Capacity</th>
                     </tr>
                  </thead>
                  <tbody>
                    {itcOps.length === 0 ? (
                      <tr><td colSpan="4" className="p-12 text-center text-slate-500 font-medium">Systemic scanners detected no immediate recovery parameters natively.</td></tr>
                    ) : (
                      itcOps.map((op, i) => (
                        <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30 transition-colors">
                          <td className="p-5 text-sm font-bold text-slate-300">{op.party}</td>
                          <td className="p-5 text-sm font-mono text-slate-400">{formatCurrency(op.original_amount)}</td>
                          <td className="p-5 text-sm text-center">
                              <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-md text-xs font-bold tracking-wider">{op.gst_rate}</span>
                          </td>
                          <td className="p-5 text-[15px] text-right font-heading font-bold text-emerald-400">+{formatCurrency(op.itc_amount)}</td>
                        </tr>
                      ))
                    )}
                    {itcOps.length > 0 && (
                      <tr className="bg-emerald-950/20 border-t border-emerald-900/30">
                         <td colSpan="3" className="p-5 text-right text-xs uppercase tracking-widest font-bold text-emerald-500/70">Aggregate Recoverable Capacity:</td>
                         <td className="p-5 text-right font-heading text-lg font-bold text-emerald-400">{formatCurrency(data?.profit_summary?.total_itc_claimable)}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
            
          </div>
        )}
      </main>
    </div>
  );
}
