import React from 'react';
import { CreditCard, Plus, Snowflake, Sun, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import { Card } from '../types';

interface CardsProps {
  cards: Card[];
  onOpenCreateCard: () => void;
  onRefresh: () => void;
}

export const Cards: React.FC<CardsProps> = ({ cards, onOpenCreateCard, onRefresh }) => {
  const handleFreeze = async (id: string) => {
    try {
      await api.freezeCard(id);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Could not freeze card');
    }
  };

  const handleUnfreeze = async (id: string) => {
    try {
      await api.unfreezeCard(id);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Could not unfreeze card');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this virtual card?')) return;
    try {
      await api.deleteCard(id);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Could not delete card');
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Virtual Cards</h1>
          <p className="text-sm text-slate-400">Issue, freeze, and manage simulated virtual cards</p>
        </div>
        <button
          onClick={onOpenCreateCard}
          data-testid="btn-create-card"
          className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold shadow-lg shadow-purple-600/20 transition flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>New Virtual Card</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((c) => (
          <div
            key={c.id}
            data-testid="card-item"
            className="bg-gradient-to-tr from-slate-900 via-slate-900 to-purple-950/40 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl flex flex-col justify-between h-56"
          >
            {/* Top row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CreditCard className="w-5 h-5 text-purple-400" />
                <span className="text-xs font-bold text-slate-300 tracking-wider uppercase">{c.card_type}</span>
              </div>
              <span
                data-testid="card-status"
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  c.status === 'ACTIVE'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }`}
              >
                {c.status}
              </span>
            </div>

            {/* Card Number */}
            <div className="my-auto">
              <div
                data-testid="card-number-masked"
                className="text-lg font-mono tracking-widest text-white font-bold"
              >
                {c.card_number_masked}
              </div>
              <div className="text-[11px] text-slate-400 mt-1">
                Limit: ${c.spending_limit.toFixed(2)}/mo
              </div>
            </div>

            {/* Bottom info & actions */}
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <div>
                <div className="text-[10px] uppercase text-slate-400 font-semibold">Cardholder</div>
                <div className="text-xs font-bold text-white">{c.cardholder_name}</div>
              </div>

              <div className="flex items-center space-x-2">
                {c.status === 'ACTIVE' ? (
                  <button
                    onClick={() => handleFreeze(c.id)}
                    data-testid="btn-freeze-card"
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs transition flex items-center space-x-1"
                    title="Freeze Card"
                  >
                    <Snowflake className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    onClick={() => handleUnfreeze(c.id)}
                    data-testid="btn-unfreeze-card"
                    className="p-1.5 rounded-lg bg-emerald-950/50 hover:bg-emerald-900/50 text-emerald-400 text-xs transition flex items-center space-x-1"
                    title="Unfreeze Card"
                  >
                    <Sun className="w-3.5 h-3.5" />
                  </button>
                )}

                <button
                  onClick={() => handleDelete(c.id)}
                  data-testid="btn-delete-card"
                  className="p-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/40 text-rose-400 text-xs transition"
                  title="Delete Card"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
