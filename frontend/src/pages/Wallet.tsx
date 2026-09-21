import React from 'react';
import { RefreshCw } from 'lucide-react';
import { WalletSummary } from '../types';

interface WalletProps {
  wallet: WalletSummary | null;
  onRefresh: () => void;
  onOpenTransfer: () => void;
}

export const Wallet: React.FC<WalletProps> = ({ wallet, onRefresh, onOpenTransfer }) => {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Multi-Currency Wallet</h1>
          <p className="text-sm text-slate-400">Isolated ledger balances with strict ACID isolation</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefresh}
            data-testid="btn-refresh-wallet"
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            title="Refresh Balances"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={onOpenTransfer}
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold transition"
          >
            Transfer Funds
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {wallet?.wallets.map((w) => (
          <div
            key={w.id}
            data-testid={`wallet-card-${w.currency}`}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                {w.currency}
              </span>
              <span className="text-xs text-slate-400">Ledger Verified</span>
            </div>

            <div className="space-y-1">
              <div className="text-xs text-slate-400">Total Balance</div>
              <div className="text-3xl font-extrabold text-white" data-testid={`wallet-balance-${w.currency}`}>
                {w.currency === 'USD' && '$'}
                {w.currency === 'EUR' && '€'}
                {w.currency === 'UAH' && '₴'}
                {w.balance.toFixed(2)}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/80 flex justify-between text-xs">
              <span className="text-slate-400">Available to Send:</span>
              <span className="font-semibold text-emerald-400">{w.available_balance.toFixed(2)} {w.currency}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
