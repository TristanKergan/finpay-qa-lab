import React, { useState, useEffect } from 'react';
import { useAuth, AuthProvider } from './context/AuthContext';
import { api } from './services/api';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { TransferModal } from './components/TransferModal';
import { CardModal } from './components/CardModal';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Wallet as WalletPage } from './pages/Wallet';
import { Transfers as TransfersPage } from './pages/Transfers';
import { Transactions as TransactionsPage } from './pages/Transactions';
import { Cards as CardsPage } from './pages/Cards';
import { Notifications as NotificationsPage } from './pages/Notifications';
import { WalletSummary, Transaction, Card, Notification } from './types';

const AppContent: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [activeTab, setActiveTab] = useState('dashboard');

  // Modals
  const [isTransferOpen, setIsTransferOpen] = useState(false);
  const [isCardOpen, setIsCardOpen] = useState(false);

  // App Data State
  const [wallet, setWallet] = useState<WalletSummary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [cards, setCards] = useState<Card[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const refreshAll = async () => {
    if (!user) return;
    try {
      const [w, tx, cd, nt] = await Promise.all([
        api.getWallet().catch(() => null),
        api.getTransactions({ page: 1, page_size: 10 }).catch(() => ({ items: [] })),
        api.getCards().catch(() => []),
        api.getNotifications().catch(() => ({ items: [], unread_count: 0 })),
      ]);
      if (w) setWallet(w);
      if (tx?.items) setTransactions(tx.items);
      if (cd) setCards(cd);
      if (nt?.items) {
        setNotifications(nt.items);
        setUnreadCount(nt.unread_count || 0);
      }
    } catch (e) {
      console.error('Error refreshing app data', e);
    }
  };

  useEffect(() => {
    if (user) {
      refreshAll();
    }
  }, [user]);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">
        Loading FinPay environment...
      </div>
    );
  }

  if (!user) {
    return authView === 'login' ? (
      <Login onNavigateToRegister={() => setAuthView('register')} />
    ) : (
      <Register onNavigateToLogin={() => setAuthView('login')} />
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar
        unreadCount={unreadCount}
        onOpenNotifications={() => setActiveTab('notifications')}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          unreadCount={unreadCount}
        />

        <main className="flex-1 overflow-y-auto p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {activeTab === 'dashboard' && (
            <Dashboard
              wallet={wallet}
              transactions={transactions}
              cards={cards}
              onOpenTransfer={() => setIsTransferOpen(true)}
              onOpenCard={() => setIsCardOpen(true)}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'wallet' && (
            <WalletPage
              wallet={wallet}
              onRefresh={refreshAll}
              onOpenTransfer={() => setIsTransferOpen(true)}
            />
          )}

          {activeTab === 'transfers' && (
            <TransfersPage
              onOpenTransfer={() => setIsTransferOpen(true)}
              transactions={transactions}
            />
          )}

          {activeTab === 'transactions' && <TransactionsPage />}

          {activeTab === 'cards' && (
            <CardsPage
              cards={cards}
              onOpenCreateCard={() => setIsCardOpen(true)}
              onRefresh={refreshAll}
            />
          )}

          {activeTab === 'notifications' && (
            <NotificationsPage
              notifications={notifications}
              onRefresh={refreshAll}
            />
          )}
        </main>
      </div>

      <TransferModal
        isOpen={isTransferOpen}
        onClose={() => setIsTransferOpen(false)}
        onSuccess={refreshAll}
      />

      <CardModal
        isOpen={isCardOpen}
        onClose={() => setIsCardOpen(false)}
        onSuccess={refreshAll}
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
