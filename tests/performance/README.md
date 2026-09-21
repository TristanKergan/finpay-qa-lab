# FinPay QA Lab - Performance Testing Guide (k6)

This directory contains automated performance tests simulating realistic fintech traffic patterns with **Grafana k6**.

## Scenarios

1. **Smoke Test (`k6-smoke.js`)**:
   - Validates system stability under light concurrency (3 VUs, 15s).
   - Thresholds: `http_req_failed < 1%`, `p(95) < 300ms`.
2. **Load Test (`k6-load.js`)**:
   - Ramps up to 30 concurrent users over 40s to measure throughput and latency under anticipated peak load.
   - Thresholds: `http_req_failed < 2%`, `p(95) < 500ms`, `p(99) < 1000ms`.
3. **Stress Test (`k6-stress.js`)**:
   - Pushes concurrency up to 100+ VUs to identify bottleneck breaking points and database connection pool saturation limits.

## How to Run

### Via local k6 binary:
```bash
# Smoke test
k6 run tests/performance/k6-smoke.js

# Load test with custom target URL
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/performance/k6-load.js

# Stress test
k6 run tests/performance/k6-stress.js
```

### Via Docker (Zero installation required):
```bash
docker run --rm -i --network="host" -v $PWD/tests/performance:/perf grafana/k6 run /perf/k6-smoke.js
```
