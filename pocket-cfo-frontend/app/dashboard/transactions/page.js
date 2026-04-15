'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { DM_Sans, Syne } from 'next/font/google';
import Sidebar from '@/components/Sidebar';
import { RefreshCw, Search, ArrowDownCircle, ArrowUpCircle } from 'lucide-react';

const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-body', weight: ['400', '500', '700'] });
const syne = Syne({ subsets: ['latin'], variable: '--font-heading', weight: ['400', '600', '700', '800'] });

const formatCurrency = (amount) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);

export default function TransactionsPage() {
  const { data: session, status } = useSession();
  const [txns, setTxns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // all, credit, debit
  
  const USER_ID = session?.user?.backend_user_id;

  useEffect(() => {
    if (status === "authenticated" && USER_ID) {
      fetchTxns();
    }
  }, [status, USER_ID]);

  const fetchTxns = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/transactions/${USER_ID}`);
      const data = await res.json();
      setTxns(data.transactions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredTxns = txns.filter(t => {
    const matchesSearch = t.party.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || t.type === filterType;
    return matchesSearch && matchesType;
  });

  if (status === "loading" || !USER_ID) {
    return <div className="min-h-screen bg-[#0D0F12] flex items-center justify-center"><RefreshCw className="animate-spin text-amber-500" size={32}/></div>;
  }

  return (
    <div className={`min-h-screen bg-[#0D0F12] text-slate-200 flex ${dmSans.variable} ${syne.variable} font-body bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]`}>
      <Sidebar />
      <main className="flex-1 ml-[240px] p-8 pb-32">
        <h1 className="font-heading text-3xl font-bold text-white mb-8">Ledger Transactions</h1>
        
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center mb-8 bg-[#111318] p-4 rounded-xl border border-slate-800 shadow-sm">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-amber-500" size={18} />
            <input 
              type="text"
              placeholder="Search by Party Name..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full bg-[#0D0F12] border border-slate-800 text-sm rounded-lg pl-10 pr-4 py-3 text-slate-200 focus:border-amber-500 outline-none transition-colors"
            />
          </div>
          <div className="flex gap-2 p-1 bg-[#0D0F12] rounded-lg border border-slate-800">
            {['all', 'credit', 'debit'].map(type => (
              <button 
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-5 py-2 rounded-md text-sm font-bold uppercase tracking-wider transition-colors ${
                  filterType === type ? 'bg-slate-800 text-amber-500 shadow-sm' : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-[#111318] border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          {loading ? (
             <div className="p-16 text-center text-slate-500 flex flex-col items-center">
                 <RefreshCw className="animate-spin text-amber-500 mb-4" size={32} /> 
                 <p className="font-medium text-slate-400">Fetching chronological ledgers...</p>
             </div>
          ) : filteredTxns.length === 0 ? (
             <div className="p-16 text-center text-slate-500">
                 <div className="bg-slate-900 w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-4">
                     <Search className="text-slate-600" size={24} />
                 </div>
                 <p className="font-medium text-slate-400">No transactions located. Modify your search boundaries or ingest new documents.</p>
             </div>
          ) : (
             <div className="overflow-x-auto custom-scrollbar">
               <table className="w-full text-left border-collapse">
                 <thead>
                   <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider">
                     <th className="p-4 font-bold">Date</th>
                     <th className="p-4 font-bold">Party</th>
                     <th className="p-4 font-bold">Amount</th>
                     <th className="p-4 font-bold">Type</th>
                     <th className="p-4 font-bold">Category</th>
                     <th className="p-4 font-bold">Source</th>
                     <th className="p-4 font-bold tracking-widest text-right">Confidence</th>
                   </tr>
                 </thead>
                 <tbody>
                   {filteredTxns.map((t, i) => (
                     <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30 transition-colors even:bg-slate-900/20 group">
                       <td className="p-4 text-sm whitespace-nowrap text-slate-400 font-mono text-xs">{t.date ? new Date(t.date).toLocaleDateString() : 'Unknown'}</td>
                       <td className="p-4 text-sm font-semibold text-slate-200 group-hover:text-amber-500 transition-colors">{t.party}</td>
                       <td className="p-4 text-sm font-bold font-heading text-[15px]">{formatCurrency(t.amount)}</td>
                       <td className="p-4 text-sm">
                         <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                           t.type === 'credit' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-500 border border-rose-500/20'
                         }`}>
                           {t.type === 'credit' ? <ArrowUpCircle size={12}/> : <ArrowDownCircle size={12}/>} {t.type}
                         </span>
                       </td>
                       <td className="p-4 text-sm text-slate-300 font-medium">{t.category}</td>
                       <td className="p-4 text-sm">
                         <span className="px-2 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded text-[10px] text-indigo-400 uppercase font-bold tracking-wider">{t.source}</span>
                       </td>
                       <td className="p-4 text-sm text-right">
                         {t.confidence > 0.8 ? (
                           <span className="text-emerald-500 font-bold text-xs bg-emerald-500/10 px-2 py-1 rounded">High ({(t.confidence*100).toFixed()}%)</span>
                         ) : t.confidence > 0.5 ? (
                           <span className="text-amber-500 font-bold text-xs bg-amber-500/10 px-2 py-1 rounded">Medium ({(t.confidence*100).toFixed()}%)</span>
                         ) : (
                           <span className="text-rose-500 font-bold text-xs bg-rose-500/10 px-2 py-1 rounded">Low ({(t.confidence*100).toFixed()}%)</span>
                         )}
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
             </div>
          )}
        </div>
      </main>
    </div>
  );
}
