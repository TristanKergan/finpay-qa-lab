import React from 'react';
import { Send, CreditCard, ArrowUpRight, ArrowDownLeft, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { WalletSummary, Transaction, Card } from '../types';

interface DashboardProps {
  wallet: WalletSummary | null;
  transactions: Transaction[];
  cards: Card[];
  onOpenTransfer: () => void;
  onOpenCard: () => void;
  onNavigateTab: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  wallet,
  transactions,
  cards,
  onOpenTransfer,
  onOpenCard,
  onNavigateTab,
}) => {
  const { user } = useAuth();

  const usdWallet = wallet?.wallets.find((w) => w.currency === 'USD');
  const eurWallet = wallet?.wallets.find((w) => w.currency === 'EUR');
  const uahWallet = wallet?.wallets.find((w) => w.currency === 'UAH');

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>FinPay Secure Account</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Welcome back, {user?.full_name || 'User'}!
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Multi-currency treasury & automated financial test bed.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenTransfer}
            data-testid="btn-quick-transfer"
            className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold shadow-lg shadow-cyan-600/20 transition flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Send Money</span>
          </button>
          <button
            onClick={onOpenCard}
            data-testid="btn-quick-card"
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-semibold transition flex items-center space-x-2"
          >
            <CreditCard className="w-4 h-4" />
            <span>New Card</span>
          </button>
        </div>
      </div>

      {/* Multi-Currency Balances */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Treasury Balances</h2>
          <div className="text-xs text-slate-400">
            Total USD Equivalent: <span data-testid="total-balance-usd" className="font-bold text-cyan-400">${wallet?.total_balance_usd.toFixed(2) || '0.00'}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* USD Card */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">USD</span>
              <span className="text-xs text-slate-400">US Dollar</span>
            </div>
            <div className="text-2xl font-black text-white" data-testid="wallet-balance-USD">
              ${usdWallet?.balance.toFixed(2) || '0.00'}
            </div>
            <div className="text-xs text-slate-400 mt-2 flex justify-between">
              <span>Available:</span>
              <span className="font-medium text-slate-200">${usdWallet?.available_balance.toFixed(2) || '0.00'}</span>
            </div>
          </div>

          {/* EUR Card */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">EUR</span>
              <span className="text-xs text-slate-400">Euro</span>
            </div>
            <div className="text-2xl font-black text-white" data-testid="wallet-balance-EUR">
              €{eurWallet?.balance.toFixed(2) || '0.00'}
            </div>
            <div className="text-xs text-slate-400 mt-2 flex justify-between">
              <span>Available:</span>
              <span className="font-medium text-slate-200">€{eurWallet?.available_balance.toFixed(2) || '0.00'}</span>
            </div>
          </div>

          {/* UAH Card */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">UAH</span>
              <span className="text-xs text-slate-400">Ukrainian Hryvnia</span>
            </div>
            <div className="text-2xl font-black text-white" data-testid="wallet-balance-UAH">
              ₴{uahWallet?.balance.toFixed(2) || '0.00'}
            </div>
            <div className="text-xs text-slate-400 mt-2 flex justify-between">
              <span>Available:</span>
              <span className="font-medium text-slate-200">₴{uahWallet?.available_balance.toFixed(2) || '0.00'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Grid for Recent Transactions & Virtual Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Transactions List */}
        <div className="lg:col-span-2 bg-slate-900/70 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-base text-white">Recent Transactions</h3>
            <button
              onClick={() => onNavigateTab('transactions')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
            >
              View All
            </button>
          </div>

          <div className="space-y-3" data-testid="recent-transactions-list">
            {transactions.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-sm">No transactions yet</div>
            ) : (
              transactions.slice(0, 5).map((t) => {
                const isIncoming = t.receiver_id === user?.id;
                return (
                  <div
                    key={t.id}
                    data-testid="recent-transaction-item"
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition"
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                          isIncoming ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                        }`}
                      >
                        {isIncoming ? <ArrowDownLeft className="w-5 h-5" /> : <ArrowUpRight className="w-5 h-5" />}
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-white">
                          {isIncoming ? `From ${t.sender_email || 'User'}` : `To ${t.receiver_email || 'User'}`}
                        </div>
                        <div className="text-[10px] text-slate-400">{new Date(t.created_at).toLocaleString()}</div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className={`text-xs font-bold ${isIncoming ? 'text-emerald-400' : 'text-slate-200'}`}>
                        {isIncoming ? '+' : '-'}{t.amount} {t.currency}
                      </div>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                          t.status === 'SUCCESS'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : t.status === 'PENDING'
                            ? 'bg-amber-500/10 text-amber-400'
                            : 'bg-rose-500/10 text-rose-400'
                        }`}
                      >
                        {t.status}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Cards Preview */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-base text-white">Active Cards</h3>
            <button
              onClick={() => onNavigateTab('cards')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
            >
              Manage
            </button>
          </div>

          <div className="space-y-3">
            {cards.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-sm">
                No cards created.
                <button
                  onClick={onOpenCard}
                  className="block mx-auto mt-2 text-xs text-cyan-400 hover:underline"
                >
                  Create your first card
                </button>
              </div>
            ) : (
              cards.slice(0, 2).map((c) => (
                <div
                  key={c.id}
                  className="p-4 rounded-xl bg-gradient-to-tr from-slate-950 to-slate-900 border border-slate-800 relative overflow-hidden"
                >
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{c.card_type}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        c.status === 'ACTIVE'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>
                  <div className="text-sm font-mono tracking-widest text-white mb-2">{c.card_number_masked}</div>
                  <div className="flex justify-between items-center text-[10px] text-slate-400">
                    <span>{c.cardholder_name}</span>
                    <span>EXP: {c.expiry_date}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
