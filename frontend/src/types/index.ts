export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  avatar_url?: string;
  status: 'ACTIVE' | 'LOCKED' | 'DELETED';
  created_at: string;
}

export interface Wallet {
  id: string;
  user_id: string;
  currency: 'USD' | 'EUR' | 'UAH';
  balance: number;
  available_balance: number;
  created_at: string;
  updated_at: string;
}

export interface WalletSummary {
  wallets: Wallet[];
  total_balance_usd: number;
}

export interface Card {
  id: string;
  user_id: string;
  card_number_masked: string;
  cardholder_name: string;
  expiry_date: string;
  card_type: 'DEBIT' | 'CREDIT' | 'VIRTUAL';
  status: 'ACTIVE' | 'FROZEN' | 'DELETED';
  spending_limit: number;
  created_at: string;
}

export interface Transaction {
  id: string;
  sender_id?: string;
  receiver_id?: string;
  sender_email?: string;
  receiver_email?: string;
  amount: number;
  currency: string;
  converted_amount: number;
  target_currency: string;
  exchange_rate: number;
  status: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | 'CANCELLED';
  idempotency_key?: string;
  description?: string;
  created_at: string;
  completed_at?: string;
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  items: Notification[];
  unread_count: number;
}
