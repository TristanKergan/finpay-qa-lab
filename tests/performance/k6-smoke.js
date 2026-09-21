import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 3, // 3 virtual users
  duration: '15s',
  thresholds: {
    http_req_failed: ['rate<0.01'], // < 1% error rate
    http_req_duration: ['p(95)<300'], // 95% of requests must complete below 300ms
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

export function setup() {
  // Login as John Doe
  const loginRes = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({
      email: 'john.doe@example.com',
      password: 'Password123!',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(loginRes, { 'login status is 200': (r) => r.status === 200 });
  const token = loginRes.json('access_token');
  return { token };
}

export default function (data) {
  const params = {
    headers: {
      Authorization: `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };

  // 1. Get Wallet
  const walletRes = http.get(`${BASE_URL}/api/v1/wallet`, params);
  check(walletRes, {
    'wallet status is 200': (r) => r.status === 200,
    'wallet has balances': (r) => r.json('wallets').length > 0,
  });

  // 2. Get Transactions
  const txRes = http.get(`${BASE_URL}/api/v1/transactions?page=1&page_size=5`, params);
  check(txRes, {
    'transactions status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
