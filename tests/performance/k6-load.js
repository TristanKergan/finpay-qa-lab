import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 10 }, // ramp-up to 10 VUs
    { duration: '20s', target: 30 }, // stay at 30 VUs
    { duration: '10s', target: 0 },  // ramp-down to 0
  ],
  thresholds: {
    http_req_failed: ['rate<0.02'], // < 2% error rate under load
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // p95 < 500ms, p99 < 1s
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

export function setup() {
  const loginRes = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({
      email: 'john.doe@example.com',
      password: 'Password123!',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

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

  // Read transactions
  const txRes = http.get(`${BASE_URL}/api/v1/transactions?page=1&page_size=10`, params);
  check(txRes, { 'tx status 200': (r) => r.status === 200 });

  // Read wallet
  const wRes = http.get(`${BASE_URL}/api/v1/wallet`, params);
  check(wRes, { 'wallet status 200': (r) => r.status === 200 });

  sleep(0.5);
}
