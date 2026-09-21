import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 },
    { duration: '15s', target: 60 },
    { duration: '15s', target: 100 }, // Stress breakpoint peak
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'], // < 5% failure under high stress
    http_req_duration: ['p(95)<1500'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

export function setup() {
  const loginRes = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({
      email: 'qa.tester@example.com',
      password: 'Password123!',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  return { token: loginRes.json('access_token') };
}

export default function (data) {
  const params = {
    headers: {
      Authorization: `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };

  const res = http.get(`${BASE_URL}/api/v1/wallet`, params);
  check(res, { 'wallet 200': (r) => r.status === 200 });

  sleep(0.2);
}
