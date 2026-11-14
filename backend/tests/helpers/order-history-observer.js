const { appendFileSync, mkdirSync, writeFileSync } = require('node:fs');
const path = require('node:path');
const { performance } = require('node:perf_hooks');
const { setTimeout: sleep } = require('node:timers/promises');
const express = require('express');
const request = require('supertest');

// Only these response fields may leave the isolated fixture. In particular,
// headers, credentials, JWTs, addresses and raw errors are never logged here.
function responseSummary(response, endpoint) {
  if (endpoint === '/api/checkout') return { order_id: response.body.orderId ?? null };
  if (!Array.isArray(response.body)) return { body_type: typeof response.body };
  return {
    order_count: response.body.length,
    orders: response.body.map(row => ({
      id: row.id, user_id: row.user_id, status: row.status, total_amount: row.total_amount,
    })),
  };
}

function createObserver(runId, directory) {
  if (!/^run-\d{2,3}$/.test(runId)) throw new Error('Invalid evidence run identifier');
  mkdirSync(directory, { recursive: true });
  const files = Object.fromEntries(['events', 'attempts', 'controls'].map(name => {
    const filename = path.join(directory, `${name}.jsonl`);
    writeFileSync(filename, '', { flag: 'wx' });
    return [name, filename];
  }));
  const origin = performance.now();
  let sequence = 0;
  const elapsed = () => Number((performance.now() - origin).toFixed(3));
  const append = (name, record) => appendFileSync(files[name], JSON.stringify(record) + '\n');
  const event = (attempt, name, details = {}) => {
    const record = {
      schema_version: 1, test_id: 'ORDER-HISTORY-01', run_id: runId, sequence: ++sequence, attempt,
      level: name === 'http.client.error' || details.status === 'failed' ? 'ERROR' : 'INFO',
      time_utc: new Date().toISOString(), elapsed_ms: elapsed(), event: name, ...details,
    };
    append('events', record);
    return record;
  };

  function transport(app, attempt, delayMs) {
    const gateway = express();
    gateway.use(async (req, res, next) => {
      const requestId = req.get('x-request-id');
      const details = { request_id: requestId, method: req.method, path: req.path };
      const received = event(attempt, 'http.server.received', details);
      res.once('finish', () => event(attempt, 'http.server.completed', {
        ...details, status_code: res.statusCode, duration_ms: Number((elapsed() - received.elapsed_ms).toFixed(3)),
      }));
      // The request is already in flight when this test-only transport waits.
      // No response/body/verdict is mocked; next() invokes the real EShop app.
      if (req.method === 'POST' && req.path === '/api/checkout') await sleep(delayMs);
      next();
    });
    gateway.use(app);
    return gateway;
  }

  async function send(gateway, token, attempt, operation, method, endpoint, body) {
    const requestId = `${runId}.a${attempt}.${operation}`;
    const details = { request_id: requestId, operation, method, path: endpoint };
    const sent = event(attempt, 'http.client.sent', details);
    try {
      let pending = request(gateway)[method.toLowerCase()](endpoint)
        .auth(token, { type: 'bearer' }).set('x-request-id', requestId)
        .timeout({ response: 3000, deadline: 4000 });
      if (body) pending = pending.send(body);
      const response = await pending;
      event(attempt, 'http.client.received', {
        ...details, status_code: response.status, duration_ms: Number((elapsed() - sent.elapsed_ms).toFixed(3)),
        response: responseSummary(response, endpoint),
      });
      return response;
    } catch (error) {
      event(attempt, 'http.client.error', { ...details, error_type: 'transport_error' });
      error.evidence = {
        category: 'transport', code: 'HTTP_TRANSPORT_ERROR',
        message: `Request ${operation} did not complete normally`,
      };
      throw error;
    }
  }

  function check(attempt, code, actual, expected) {
    try {
      expect(actual).toEqual(expected);
      event(attempt, 'assertion.completed', { assertion_id: code, status: 'passed', expected, actual });
    } catch (error) {
      error.evidence = {
        category: 'assertion', code,
        message: `${code}: expected ${JSON.stringify(expected)}, received ${JSON.stringify(actual)}`,
        expected, actual,
      };
      event(attempt, 'assertion.completed', { assertion_id: code, status: 'failed', expected, actual });
      throw error;
    }
  }

  return { event, append, elapsed, transport, send, check };
}

module.exports = { createObserver };
