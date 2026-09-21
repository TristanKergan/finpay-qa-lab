import React from 'react';
import { LayoutDashboard, Wallet, ArrowRightLeft, CreditCard, History, Bell } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  unreadCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, unreadCount }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'wallet', label: 'Wallet', icon: Wallet },
    { id: 'transfers', label: 'Transfers', icon: ArrowRightLeft },
    { id: 'transactions', label: 'Transactions', icon: History },
    { id: 'cards', label: 'Virtual Cards', icon: CreditCard },
    { id: 'notifications', label: 'Notifications', icon: Bell, badge: unreadCount },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col p-4 space-y-1">
      <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">Main Navigation</div>
      {menuItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            data-testid={`tab-${item.id}`}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl font-medium text-sm transition ${
              isActive
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center space-x-3">
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </div>
            {item.badge !== undefined && item.badge > 0 && (
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                {item.badge}
              </span>
            )}
          </button>
        );
      })}
    </aside>
  );
};
