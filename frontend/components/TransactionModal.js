"use client";
import { useState, useRef } from 'react';
import { financeAPI } from '@/lib/api';
import { X, UploadCloud, FileText, Bot, PenTool, Loader2, CheckCircle2 } from 'lucide-react';

export default function TransactionModal({ isOpen, onClose, onSuccess }) {
  const [mode, setMode] = useState('ai'); 
  const [step, setStep] = useState('upload'); 
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    merchant: '',
    date: new Date().toISOString().split('T')[0], 
    amount: '',
    category: 'Food & Dining',
  });

  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setStep('processing');
    setError('');

    try {
      const res = await financeAPI.uploadReceipt(file);
      
      setFormData({
        merchant: res.data.merchant || '',
        date: res.data.date || new Date().toISOString().split('T')[0],
        amount: res.data.amount || '',
        category: res.data.category || 'Food & Dining',
      });
      
      setStep('verify');
    } catch (err) {
      console.error(err);
      setError("AI failed to read the receipt. Please enter manually.");
      setMode('manual');
      setStep('verify');
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      await financeAPI.saveTransaction({
        ...formData,
        category_id: formData.category,
        amount: parseFloat(formData.amount),
        type: "expense" 
      });
      
      onSuccess(); 
      resetAndClose();
    } catch (err) {
      console.error("FastAPI Error Details:", err.response?.data?.detail);
      
      if (err.response?.status === 422) {
        const errorDetail = err.response.data.detail[0];
        setError(`Schema Error: '${errorDetail.loc[errorDetail.loc.length - 1]}' - ${errorDetail.msg}`);
      } else {
        setError("Failed to save transaction.");
      }
    }
  };

  const resetAndClose = () => {
    setStep('upload');
    setMode('ai');
    setFormData({ merchant: '', date: '', amount: '', category: 'Food & Dining' });
    setError('');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
        
        <div className="flex justify-between items-center p-6 border-b border-slate-100">
          <h2 className="text-xl font-bold text-slate-800">New Transaction</h2>
          <button onClick={resetAndClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="p-6">
          {error && <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-xl">{error}</div>}

          {/* Step 1: Upload (AI Mode) */}
          {mode === 'ai' && step === 'upload' && (
            <div className="space-y-6">
              <div className="flex bg-slate-100 p-1 rounded-xl">
                <button className="flex-1 py-2 bg-white shadow-sm rounded-lg text-sm font-bold text-blue-600 flex items-center justify-center gap-2">
                  <Bot size={18} /> AI Scan
                </button>
                <button onClick={() => { setMode('manual'); setStep('verify'); }} className="flex-1 py-2 text-sm font-medium text-slate-500 hover:text-slate-700 flex items-center justify-center gap-2 transition-all">
                  <PenTool size={18} /> Manual
                </button>
              </div>

              <div 
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-blue-200 rounded-2xl h-48 flex flex-col items-center justify-center text-blue-600 hover:bg-blue-50 hover:border-blue-400 transition-all cursor-pointer group"
              >
                <UploadCloud size={48} className="mb-4 text-blue-400 group-hover:scale-110 transition-transform" />
                <p className="font-semibold text-lg">Click or Drag receipt</p>
                <p className="text-sm text-blue-400 mt-1">Supports JPG, PNG, PDF</p>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileUpload} 
                  className="hidden" 
                  accept="image/*,.pdf" 
                />
              </div>
            </div>
          )}

          {step === 'processing' && (
            <div className="h-48 flex flex-col items-center justify-center text-blue-600 space-y-4">
              <Loader2 size={48} className="animate-spin" />
              <p className="font-bold animate-pulse">AI is analyzing your receipt...</p>
            </div>
          )}

          {step === 'verify' && (
            <form onSubmit={handleSave} className="space-y-4 animate-in slide-in-from-right-4">
              {mode === 'ai' && (
                <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 p-3 rounded-xl mb-4">
                  <CheckCircle2 size={20} />
                  <span className="text-sm font-medium">Scan complete. Please verify details.</span>
                </div>
              )}

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Merchant</label>
                <input type="text" value={formData.merchant} onChange={(e) => setFormData({...formData, merchant: e.target.value})} className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none" required />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Amount</label>
                  <input type="number" step="0.01" value={formData.amount} onChange={(e) => setFormData({...formData, amount: e.target.value})} className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none" required />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Date</label>
                  <input type="date" value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none" required />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Category</label>
                <select value={formData.category} onChange={(e) => setFormData({...formData, category: e.target.value})} className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none">
                  <option>Food & Dining</option>
                  <option>Transport</option>
                  <option>Shopping</option>
                  <option>Utilities</option>
                  <option>Entertainment</option>
                </select>
              </div>

              <button type="submit" className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg transition-all mt-4">
                Save Transaction
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}