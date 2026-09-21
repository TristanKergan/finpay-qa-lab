import React from 'react';
import { Bell, LogOut, Shield, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface NavbarProps {
  unreadCount: number;
  onOpenNotifications: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ unreadCount, onOpenNotifications }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-lg text-white tracking-tight">FinPay</span>
          <span className="text-xs font-semibold px-2 py-0.5 ml-2 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">QA LAB</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <button
          onClick={onOpenNotifications}
          data-testid="btn-notifications"
          className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title="Notifications"
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span
              data-testid="unread-badge"
              className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center ring-2 ring-slate-900 animate-pulse"
            >
              {unreadCount}
            </span>
          )}
        </button>

        {user && (
          <div className="flex items-center space-x-3 pl-2 border-l border-slate-800">
            <div
              data-testid="user-avatar"
              className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400 font-semibold text-xs"
            >
              {user.avatar_url ? (
                <img src={user.avatar_url} alt="avatar" className="w-full h-full rounded-full object-cover" />
              ) : (
                user.full_name?.slice(0, 2).toUpperCase() || <UserIcon className="w-4 h-4" />
              )}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-medium text-slate-200" data-testid="user-full-name">{user.full_name}</div>
              <div className="text-[10px] text-slate-400 truncate max-w-[130px]">{user.email}</div>
            </div>
            <button
              onClick={() => logout()}
              data-testid="btn-logout"
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
