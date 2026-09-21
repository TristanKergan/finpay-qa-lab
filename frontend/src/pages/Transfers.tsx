import React from 'react';
import { Send } from 'lucide-react';
import { Transaction } from '../types';

interface TransfersProps {
  onOpenTransfer: () => void;
  transactions: Transaction[];
}

export const Transfers: React.FC<TransfersProps> = ({ onOpenTransfer }) => {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Transfers Hub</h1>
          <p className="text-sm text-slate-400">Initiate and monitor peer-to-peer payments</p>
        </div>
        <button
          onClick={onOpenTransfer}
          data-testid="btn-initiate-transfer"
          className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold shadow-lg shadow-cyan-600/20 transition flex items-center space-x-2"
        >
          <Send className="w-4 h-4" />
          <span>New Transfer</span>
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-base font-bold text-white mb-4">Transfer Guidelines & QA Scenarios</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="font-bold text-cyan-400 mb-1">Idempotency Protection</div>
            <p className="text-slate-400">Replaying the same idempotency key prevents duplicate charges and ensures safe network retries.</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="font-bold text-cyan-400 mb-1">Currency Conversion</div>
            <p className="text-slate-400">Transfers between different currencies calculate live exchange rates between USD, EUR, and UAH.</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="font-bold text-cyan-400 mb-1">Defect Injection (BUG_MODE)</div>
            <p className="text-slate-400">When BUG_MODE=true is active, negative transfers, self-transfers, or rate flips can be tested.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
