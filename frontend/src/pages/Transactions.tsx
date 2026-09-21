import React, { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight, RefreshCw, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { TransactionListResponse } from '../types';

export const Transactions: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<TransactionListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(6);
  const [statusFilter, setStatusFilter] = useState('');
  const [currencyFilter, setCurrencyFilter] = useState('');
  const [search, setSearch] = useState('');

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {
        page,
        page_size: pageSize,
      };
      if (statusFilter) params.status = statusFilter;
      if (currencyFilter) params.currency = currencyFilter;

      const res = await api.getTransactions(params);
      setData(res);
    } catch (err) {
      console.error('Error fetching transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, statusFilter, currencyFilter]);

  const filteredItems = data?.items.filter((item) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      item.description?.toLowerCase().includes(q) ||
      item.sender_email?.toLowerCase().includes(q) ||
      item.receiver_email?.toLowerCase().includes(q) ||
      item.id.toLowerCase().includes(q) ||
      item.currency.toLowerCase().includes(q)
    );
  }) || [];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Transaction History</h1>
          <p className="text-sm text-slate-400">Ledger entries with full audit trail and idempotency tracking</p>
        </div>
        <button
          onClick={fetchTransactions}
          data-testid="btn-refresh-txns"
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition self-start sm:self-auto"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            data-testid="input-search-txns"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search description, recipient, sender, ID..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center space-x-3">
          <select
            data-testid="filter-status"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="SUCCESS">SUCCESS</option>
            <option value="PENDING">PENDING</option>
            <option value="FAILED">FAILED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>

          <select
            data-testid="filter-currency"
            value={currencyFilter}
            onChange={(e) => {
              setCurrencyFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Currencies</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="UAH">UAH</option>
          </select>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Counterparty</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No transactions match the selected criteria.
                  </td>
                </tr>
              ) : (
                filteredItems.map((t) => {
                  const isIncoming = t.receiver_id === user?.id;
                  return (
                    <tr
                      key={t.id}
                      data-testid="transaction-row"
                      className="hover:bg-slate-800/30 transition"
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <div
                            className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                              isIncoming ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                            }`}
                          >
                            {isIncoming ? <ArrowDownLeft className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}
                          </div>
                          <span className="text-xs font-semibold">{isIncoming ? 'Received' : 'Sent'}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-medium text-white text-xs">
                          {isIncoming ? t.sender_email || 'System' : t.receiver_email || 'Unknown'}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-400 truncate max-w-xs">
                        {t.description || '—'}
                      </td>
                      <td className="py-3 px-4">
                        <div
                          data-testid="transaction-amount"
                          className={`font-bold text-xs ${isIncoming ? 'text-emerald-400' : 'text-slate-200'}`}
                        >
                          {isIncoming ? '+' : '-'}{t.amount.toFixed(2)} {t.currency}
                        </div>
                        {t.currency !== t.target_currency && (
                          <div className="text-[10px] text-slate-400">
                            ≈ {t.converted_amount.toFixed(2)} {t.target_currency}
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          data-testid="transaction-status"
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                            t.status === 'SUCCESS'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              : t.status === 'PENDING'
                              ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                              : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                          }`}
                        >
                          {t.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-400 whitespace-nowrap">
                        {new Date(t.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-950/40 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing <span className="text-white font-medium">{filteredItems.length}</span> of{' '}
            <span className="text-white font-medium">{data?.total || 0}</span> transactions
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              data-testid="btn-prev-page"
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span data-testid="text-current-page" className="px-2 font-medium text-slate-200">
              Page {data?.page || 1} of {data?.total_pages || 1}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(data?.total_pages || 1, p + 1))}
              disabled={page >= (data?.total_pages || 1)}
              data-testid="btn-next-page"
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
