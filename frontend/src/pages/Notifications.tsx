import React from 'react';
import { Bell, Check, CheckCheck } from 'lucide-react';
import { api } from '../services/api';
import { Notification } from '../types';

interface NotificationsProps {
  notifications: Notification[];
  onRefresh: () => void;
}

export const Notifications: React.FC<NotificationsProps> = ({ notifications, onRefresh }) => {
  const handleMarkRead = async (id: string) => {
    try {
      await api.markNotificationRead(id);
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Notification Center</h1>
          <p className="text-sm text-slate-400">Security alerts, incoming payments, and transaction notices</p>
        </div>
        <button
          onClick={handleMarkAllRead}
          data-testid="btn-mark-all-read"
          className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition flex items-center space-x-2"
        >
          <CheckCheck className="w-4 h-4 text-cyan-400" />
          <span>Mark All as Read</span>
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl divide-y divide-slate-800/80 overflow-hidden shadow-lg">
        {notifications.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">
            No notifications available.
          </div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              data-testid="notification-item"
              className={`p-4 flex items-start justify-between transition ${
                n.is_read ? 'bg-slate-900/40 opacity-75' : 'bg-cyan-950/20'
              }`}
            >
              <div className="flex items-start space-x-3.5">
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                    n.is_read ? 'bg-slate-800 text-slate-400' : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  }`}
                >
                  <Bell className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-white">{n.title}</span>
                    {!n.is_read && (
                      <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    )}
                  </div>
                  <p className="text-xs text-slate-300 mt-1">{n.message}</p>
                  <div className="text-[10px] text-slate-400 mt-1.5">{new Date(n.created_at).toLocaleString()}</div>
                </div>
              </div>

              {!n.is_read && (
                <button
                  onClick={() => handleMarkRead(n.id)}
                  data-testid="btn-mark-read"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition"
                  title="Mark as read"
                >
                  <Check className="w-4 h-4" />
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
