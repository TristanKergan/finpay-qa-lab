import React, { useState } from 'react';
import { X, CreditCard, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface CardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const CardModal: React.FC<CardModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [cardholderName, setCardholderName] = useState('');
  const [cardType, setCardType] = useState('VIRTUAL');
  const [spendingLimit, setSpendingLimit] = useState('1000');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await api.createCard({
        cardholder_name: cardholderName,
        card_type: cardType,
        spending_limit: parseFloat(spendingLimit) || 1000,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create card');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-white">Create Virtual Card</h3>
              <p className="text-xs text-slate-400">Generate a safe, masked virtual card for testing</p>
            </div>
          </div>
          <button
            onClick={onClose}
            data-testid="btn-close-card"
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Cardholder Name</label>
            <input
              type="text"
              required
              data-testid="input-cardholder-name"
              value={cardholderName}
              onChange={(e) => setCardholderName(e.target.value)}
              placeholder="e.g. JOHN DOE"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Card Type</label>
            <select
              data-testid="select-card-type"
              value={cardType}
              onChange={(e) => setCardType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-purple-500"
            >
              <option value="VIRTUAL">Virtual</option>
              <option value="DEBIT">Debit</option>
              <option value="CREDIT">Credit</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Monthly Spending Limit ($)</label>
            <input
              type="number"
              min="1"
              required
              data-testid="input-spending-limit"
              value={spendingLimit}
              onChange={(e) => setSpendingLimit(e.target.value)}
              placeholder="1000"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-purple-500"
            />
          </div>

          <div className="pt-2 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-slate-800 text-slate-300 text-sm font-medium hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              data-testid="btn-submit-card"
              className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold shadow-lg shadow-purple-600/20 transition disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Issue Card'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
