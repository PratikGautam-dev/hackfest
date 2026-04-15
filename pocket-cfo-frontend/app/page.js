'use client';

import { useState, useEffect } from 'react';
import { DM_Sans, Syne } from 'next/font/google';
import { 
  LayoutDashboard, 
  LineChart, 
  FileText, 
  RefreshCw, 
  Send,
  User,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  TrendingDown,
  CheckCircle,
  MessageSquare
} from 'lucide-react';

const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-body', weight: ['400', '500', '700'] });
const syne = Syne({ subsets: ['latin'], variable: '--font-heading', weight: ['400', '600', '700', '800'] });

const USER_ID = "demo_hackathon_user";

// Format Currency
const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '₹0.00';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
  }).format(amount);
};

// UI Components (Emulating shadcn)
const Skeleton = ({ className }) => (
  <div className={`animate-pulse rounded-md bg-slate-800 ${className}`} />
);

export default function PocketCFODashboard() {
  const [actions, setActions] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [currentDate, setCurrentDate] = useState('');
  
  // SMS Parsing State
  const [isSmsPanelOpen, setIsSmsPanelOpen] = useState(false);
  const [smsText, setSmsText] = useState('');
  const [parsingSms, setParsingSms] = useState(false);
  const [smsResult, setSmsResult] = useState(null);

  const fetchData = async () => {
    setRefreshing(true);
    try {
      const [actionsRes, insightsRes] = await Promise.all([
        fetch(`http://localhost:8000/actions/${USER_ID}`),
        fetch(`http://localhost:8000/insights/${USER_ID}`)
      ]);
      
      const actionsData = await actionsRes.json();
      const insightsData = await insightsRes.json();
      
      setActions(actionsData.actions || []);
      setInsights(insightsData.profit_summary || null);
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const dateOpts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    setCurrentDate(new Date().toLocaleDateString('en-IN', dateOpts));
  }, []);

  const handleSmsSubmit = async () => {
    if (!smsText.trim()) return;
    setParsingSms(true);
    try {
      const res = await fetch(`http://localhost:8000/ingest/sms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: USER_ID, text: smsText })
      });
      const data = await res.json();
      setSmsResult(data);
    } catch (err) {
      console.error(err);
      setSmsResult({ error: "Failed to parse SMS." });
    } finally {
      setParsingSms(false);
    }
  };

  return (
    <div className={`min-h-screen bg-[#0D0F12] text-slate-200 flex ${dmSans.variable} ${syne.variable} font-body bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]`}>
      
      {/* Sidebar */}
      <aside className="w-[240px] fixed inset-y-0 left-0 bg-[#111318] border-r border-slate-800 flex flex-col z-20">
        <div className="p-6">
          <div className="flex items-center gap-3 text-amber-500 font-heading font-bold text-2xl tracking-tight">
            <span>₹</span>
            <span className="text-white">Pocket CFO</span>
          </div>
          <p className="text-xs text-slate-500 mt-2 font-medium uppercase tracking-wider">Command Center</p>
        </div>
        
        <nav className="flex-1 px-4 space-y-2 mt-4">
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-amber-500/10 text-amber-500 font-medium transition-colors">
            <LayoutDashboard size={18} /> Dashboard
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium transition-colors">
            <LineChart size={18} /> Insights
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium transition-colors">
            <FileText size={18} /> ITC / GST
          </a>
        </nav>
        
        <div className="p-4 border-t border-slate-800 mb-6 mx-4 rounded-xl bg-slate-900 flex items-center gap-3 shadow-inner">
          <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">
            <User size={18} />
          </div>
          <div className="flex-1 overflow-hidden">
            <h4 className="text-sm font-semibold text-white truncate">Demo Account</h4>
            <p className="text-xs text-slate-500 truncate">{USER_ID}</p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 ml-[240px] flex flex-col relative pb-32">
        {/* Topbar */}
        <header className="h-[72px] flex items-center justify-between px-8 bg-[#0D0F12]/80 backdrop-blur-md sticky top-0 z-10 border-b border-slate-800">
          <div className="font-medium text-slate-400 text-sm">{currentDate}</div>
          <button 
            onClick={fetchData}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-semibold transition-all disabled:opacity-50"
          >
            <RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />
            Refresh Data
          </button>
        </header>

        <div className="p-8">
          {/* Summary Stats Row */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            {[
              { label: "Total Revenue", value: insights?.total_revenue, delay: "0" },
              { label: "Total Expenses", value: insights?.total_expenses, delay: "100" },
              { label: "Net Profit", value: insights?.net_profit, delay: "200" },
              { label: "ITC Claimable", value: insights?.total_itc_claimable, delay: "300" },
            ].map((stat, idx) => (
              <div key={idx} className="bg-[#111318] border border-slate-800 rounded-xl p-6 shadow-sm flex flex-col">
                <span className="text-sm text-slate-500 font-medium tracking-wide">{stat.label}</span>
                {loading ? (
                  <Skeleton className="h-8 w-24 mt-3 rounded" />
                ) : (
                  <span className={`text-3xl font-heading font-bold mt-2 ${stat.label === "Net Profit" && stat.value < 0 ? 'text-red-500' : 'text-slate-100'}`}>
                    {formatCurrency(stat.value)}
                  </span>
                )}
              </div>
            ))}
          </section>

          {/* Actions Grid */}
          <section>
            <h2 className="font-heading text-2xl font-bold text-white mb-6">Action Hub</h2>
            {loading ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-40 rounded-xl" />)}
              </div>
            ) : actions.length === 0 ? (
              <div className="bg-[#111318] border border-slate-800 rounded-xl p-12 text-center">
                <CheckCircle size={48} className="mx-auto text-emerald-500 mb-4 opacity-50" />
                <h3 className="text-xl font-heading font-semibold text-slate-200">All Caught Up</h3>
                <p className="text-slate-500 mt-2 font-medium">No actions or anomalies detected for this period.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
                {['red', 'amber', 'green'].map(priority => {
                  const items = actions.filter(a => a.priority === priority);
                  if (items.length === 0) return null;
                  return items.map((action, idx) => {
                    
                    const styling = {
                      red: "border-l-4 border-red-500 bg-red-950/20",
                      amber: "border-l-4 border-amber-500 bg-amber-950/20",
                      green: "border-l-4 border-green-500 bg-green-950/20"
                    }[priority];
                    
                    const BadgeIcon = priority === 'red' ? AlertCircle : (priority === 'amber' ? TrendingDown : CheckCircle);
                    
                    return (
                      <div 
                        key={idx} 
                        className={`rounded-xl border border-slate-800/60 p-6 transition-transform hover:-translate-y-1 shadow-md ${styling}`}
                      >
                        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold mb-4 uppercase tracking-wider
                          ${priority === 'red' ? 'bg-red-500/20 text-red-500' : 
                            priority === 'amber' ? 'bg-amber-500/20 text-amber-500' : 'bg-green-500/20 text-green-500'}`}
                        >
                          <BadgeIcon size={12} strokeWidth={3} />
                          {priority === 'red' ? 'Urgent' : priority === 'amber' ? 'Watch' : 'Opportunity'}
                        </div>
                        <h3 className="font-heading text-lg font-bold text-slate-100 leading-snug mb-2">
                          {action.title}
                        </h3>
                        <p className="text-sm text-slate-400 font-medium leading-relaxed">
                          {action.message}
                        </p>
                        {action.amount !== null && (
                          <div className="mt-5">
                            <span className="font-heading text-2xl font-bold text-amber-500">
                              {formatCurrency(action.amount)}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  });
                })}
              </div>
            )}
          </section>
        </div>
      </main>

      {/* Fixed Collapsible SMS Ingest Panel */}
      <div className={`fixed bottom-0 right-0 left-[240px] bg-[#111318] border-t border-slate-800 z-30 transition-all duration-300 ${isSmsPanelOpen ? 'translate-y-0' : 'translate-y-[calc(100%-60px)]'}`}>
        <button 
          onClick={() => setIsSmsPanelOpen(!isSmsPanelOpen)}
          className="w-full h-[60px] flex items-center justify-between px-8 text-slate-300 hover:bg-slate-800/50 transition-colors focus:outline-none"
        >
          <div className="flex items-center gap-3 font-heading font-bold text-lg">
            <MessageSquare size={20} className="text-amber-500" />
            Quick SMS Ingest
          </div>
          {isSmsPanelOpen ? <ChevronDown size={20} /> : <ChevronUp size={20} />}
        </button>
        
        <div className="px-8 pb-8 pt-2 h-[280px] overflow-y-auto custom-scrollbar">
          <div className="flex flex-col gap-4">
            <textarea 
              value={smsText}
              onChange={(e) => setSmsText(e.target.value)}
              placeholder="Paste raw bank SMS text here..."
              className="w-full h-24 bg-[#0D0F12] border border-slate-800 rounded-xl p-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all resize-none text-sm font-medium"
            />
            <button 
              onClick={handleSmsSubmit}
              disabled={parsingSms || !smsText.trim()}
              className="flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold py-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {parsingSms ? <RefreshCw size={18} className="animate-spin" /> : <Send size={18} />}
              Parse Transaction
            </button>
            
            {smsResult && (
              <div className="mt-2 text-sm bg-slate-900 border border-slate-800 rounded-lg p-4 h-full">
                {smsResult.error ? (
                  <p className="text-red-400 flex items-center gap-2"><AlertCircle size={16}/> {smsResult.error}</p>
                ) : smsResult.status === "skipped" ? (
                  <p className="text-slate-500 flex items-center gap-2"><CheckCircle size={16}/> Ignored: {smsResult.reason}</p>
                ) : (
                  <div className="text-emerald-400">
                    <p className="flex items-center gap-2 font-bold mb-1"><CheckCircle size={16}/> Parsed Successfully!</p>
                    <p className="text-slate-300 font-mono text-xs">Category: {smsResult.category} | Amount: ₹{smsResult.amount} | Type: {smsResult.type}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
