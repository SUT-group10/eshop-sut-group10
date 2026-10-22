const { randomInt } = require('node:crypto');
const { performance } = require('node:perf_hooks');
const { setTimeout: sleep } = require('node:timers/promises');
const request = require('supertest');
const { createHarness } = require('../helpers/harness');

const FAST_DELAY_MS = 60;
const SLOW_DELAY_MS = 160;
const READ_WAIT_MS = 100;

test('E-01 cart contains the product after a fixed wait (injected timing flake)', async () => {
  const mode = process.env.FLAKE_LATENCY_MODE || 'sampled';
  if (!['sampled', 'fast', 'slow'].includes(mode)) {
    throw new Error('FLAKE_LATENCY_MODE must be sampled, fast or slow');
  }
  // Sample only the delay before the real HTTP request, never its result.
  const selectedCase = mode === 'sampled'
    ? (randomInt(2) === 0 ? 'fast' : 'slow') : mode;
  const delayMs = selectedCase === 'fast' ? FAST_DELAY_MS : SLOW_DELAY_MS;
  const harness = await createHarness();
  let pendingAdd;
  try {
    const user = await harness.login();
    const product = await harness.product();
    const started = performance.now();
    const elapsed = () => Number((performance.now() - started).toFixed(3));
    const timeline = {};

    // Start A now. Do not await completion before starting B's fixed wait.
    // Capture errors immediately so a background rejection cannot go unhandled.
    pendingAdd = (async () => {
      await sleep(delayMs);
      timeline.addSentMs = elapsed();
      const response = await request(harness.app).post('/api/cart')
        .auth(user.token, { type: 'bearer' }).send({ ...product, quantity: 1 });
      timeline.addCompletedMs = elapsed();
      console.info('E-01 add completed ' + JSON.stringify({ ...timeline, httpStatus: response.status }));
      return response;
    })().then(response => ({ response }), error => ({ error }));

    // Intentional defect: elapsed time is used instead of completion of A.
    await sleep(READ_WAIT_MS);
    timeline.readSentMs = elapsed();
    const cart = await request(harness.app).get('/api/cart')
      .auth(user.token, { type: 'bearer' });
    timeline.readCompletedMs = elapsed();
    console.info('E-01 observation ' + JSON.stringify({
      mode, selectedCase, delayMs,
      readWaitMs: READ_WAIT_MS, ...timeline, httpStatus: cart.status,
      cart: cart.body,
    }));
    expect(cart.status).toBe(200);
    expect(cart.body).toHaveLength(1);
    expect(cart.body[0]).toMatchObject({ id: product.id, quantity: 1 });
  } finally {
    // Even a failed assertion must drain A before closing its isolated fixture.
    try {
      if (pendingAdd) {
        const outcome = await pendingAdd;
        expect(outcome.error).toBeUndefined();
        expect(outcome.response.status).toBe(200);
      }
    } finally {
      await harness.close();
    }
  }
});
