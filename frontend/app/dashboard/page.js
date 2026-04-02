"use client";
import { useEffect, useState } from "react";
import { financeAPI } from "@/lib/api";
import { ArrowUpRight, ArrowDownRight, Wallet, Loader2, Receipt } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export default function Dashboard() {
  const [summary, setSummary] = useState({ total_income: 0, total_expense: 0, net_balance: 0 });
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [sumRes, catRes, txRes] = await Promise.all([
          financeAPI.getSummary().catch(() => ({ data: { total_income: 0, total_expense: 0, net_balance: 0 } })),
          financeAPI.getCategories().catch(() => ({ data: [] })),
          financeAPI.getTransactions() // <-- NEW: Fetch the ledger
        ]);
        
        setSummary(sumRes.data);
        setTransactions(txRes.data);
        
        const chartData = catRes.data.map(item => ({
          name: item.category,
          value: item.total_amount
        }));
        setCategories(chartData);

      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const stats = [
    { label: "Total Income", value: summary.total_income, icon: ArrowUpRight, color: "text-emerald-600", bg: "bg-emerald-50" },
    { label: "Total Expenses", value: summary.total_expense, icon: ArrowDownRight, color: "text-rose-600", bg: "bg-rose-50" },
    { label: "Net Balance", value: summary.net_balance, icon: Wallet, color: "text-blue-600", bg: "bg-blue-50" },
  ];

  if (loading) return (
    <div className="h-[60vh] flex flex-col items-center justify-center gap-4">
      <Loader2 className="animate-spin text-blue-600" size={40} />
      <p className="text-slate-500 font-medium">Crunching the numbers...</p>
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg ${stat.bg} ${stat.color}`}>
                <stat.icon size={24} />
              </div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Monthly</span>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">{stat.label}</p>
              <h3 className="text-3xl font-bold text-slate-900">
                ${stat.value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </h3>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold text-slate-800 mb-6">Spending by Category</h3>
          <div className="w-full min-h-[300px] min-w-0">
            {categories.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={categories} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                    {categories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-slate-400 italic">No expense data found.</div>
            )}
          </div>
        </div>

        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-center">
          <h3 className="text-lg font-bold text-slate-800 mb-6">CFO Insights</h3>
          <div className="bg-blue-50 border border-blue-100 p-6 rounded-xl">
            <p className="text-blue-800 leading-relaxed font-medium">
              "You recently scanned a receipt for <span className="font-bold underline">${transactions[0]?.amount || 0}</span> from <span className="font-bold">{transactions[0]?.merchant || 'a store'}</span>. Keep scanning to unlock more AI insights!"
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Receipt size={20} className="text-blue-600"/> 
            Recent Transactions
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4 font-semibold">Date</th>
                <th className="p-4 font-semibold">Merchant</th>
                <th className="p-4 font-semibold">Category</th>
                <th className="p-4 font-semibold text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {transactions.length > 0 ? (
                transactions.map((tx) => (
                  <tr key={tx._id || tx.id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 text-sm text-slate-600">
                      {new Date(tx.date).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-sm font-medium text-slate-900">{tx.merchant}</td>
                    <td className="p-4">
                      <span className="px-3 py-1 bg-slate-100 text-slate-600 text-xs rounded-full font-medium">
                        {tx.category || tx.category_id}
                      </span>
                    </td>
                    <td className="p-4 text-sm font-bold text-slate-900 text-right">
                      ${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="p-8 text-center text-slate-400 italic">
                    No transactions yet. Click "New Receipt" to add one!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}