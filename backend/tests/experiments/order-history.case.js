const path = require('node:path');
const { randomInt } = require('node:crypto');
const { setTimeout: sleep } = require('node:timers/promises');
const request = require('supertest');
const { createHarness } = require('../helpers/harness');
const { createObserver } = require('../helpers/order-history-observer');

const variant = process.env.ORDER_TEST_VARIANT || 'timed';
const retryLimit = Number(process.env.ORDER_TEST_RETRIES ?? '2');
const observationWaitMs = 120;
const replayDelays = process.env.ORDER_TRANSPORT_DELAYS?.split(',').map(Number);
if (!['timed', 'awaited'].includes(variant) || ![0, 1, 2].includes(retryLimit) ||
    (replayDelays && (replayDelays.length < retryLimit + 1 ||
      replayDelays.some(value => !Number.isInteger(value) || value < 0 || value > 2000)))) {
  throw new Error('Invalid order-history experiment configuration');
}
const observer = createObserver(process.env.ORDER_RUN_ID || 'run-01',
  process.env.ORDER_EVIDENCE_DIR || path.resolve('test-results/order-history', `direct-${Date.now()}`));

// Jest itself retries the complete test body. The test never chooses its verdict.
jest.retryTimes(retryLimit, { logErrorsBeforeRetry: true, retryImmediately: true });
let invocation = 0;

test('Submitted order appears in account history', async () => {
  const attempt = ++invocation;
  const fixtureId = `fixture-${attempt}`;
  const started = observer.event(attempt, 'attempt.started', {
    fixture_id: fixtureId, retry_of_attempt: attempt === 1 ? null : attempt - 1,
  });
  const delayMs = replayDelays ? replayDelays[attempt - 1] : randomInt(20, 221);
  observer.append('controls', { attempt, variant, transport_delay_ms: delayMs, observation_wait_ms: observationWaitMs });
  let harness;
  let pendingSubmit;
  let failure;
  let phase = 'setup';
  let observedCount = null;
  let verifiedCount = null;
  let additionalFailure = null;
  try {
    harness = await createHarness();
    const user = await harness.login();
    const product = await harness.product();
    const cart = await request(harness.app).post('/api/cart')
      .auth(user.token, { type: 'bearer' }).send({ ...product, quantity: 1 });
    observer.check(attempt, 'FIXTURE_CART_HTTP', cart.status, 200);
    const initial = await harness.get('SELECT COUNT(*) AS count FROM orders');
    observer.check(attempt, 'FIXTURE_ORDER_COUNT', initial.count, 0);
    observer.event(attempt, 'fixture.ready', { fixture_id: fixtureId, initial_order_count: initial.count });
    const gateway = observer.transport(harness.app, attempt, delayMs);
    phase = 'execution';
    pendingSubmit = observer.send(gateway, user.token, attempt, 'submit', 'POST', '/api/checkout', {
      total_amount: product.price, shipping_address: 'Isolated fixture address',
    }).then(response => ({ response }), error => ({ error }));

    if (variant === 'awaited') {
      const submitted = await pendingSubmit;
      if (submitted.error) throw submitted.error;
      observer.check(attempt, 'SUBMIT_HTTP', submitted.response.status, 200);
    } else {
      // Deliberately incorrect synchronization for the experiment's baseline.
      // A duration is not evidence that the submitted order is ready to read.
      await sleep(observationWaitMs);
    }
    const observed = await observer.send(gateway, user.token, attempt, 'history', 'GET', '/api/orders/my-orders');

    // Preserve the first snapshot. Drain the write and probe independently;
    // later visibility must never turn an earlier failed assertion into PASS.
    const submitted = await pendingSubmit;
    if (submitted.error) throw submitted.error;
    if (variant !== 'awaited') observer.check(attempt, 'SUBMIT_HTTP', submitted.response.status, 200);
    const verified = await observer.send(gateway, user.token, attempt, 'confirmation', 'GET', '/api/orders/my-orders');
    phase = 'verification';
    observer.check(attempt, 'HISTORY_HTTP', observed.status, 200);
    observer.check(attempt, 'CONFIRMATION_HTTP', verified.status, 200);
    observer.check(attempt, 'HISTORY_BODY_IS_ARRAY', Array.isArray(observed.body), true);
    observer.check(attempt, 'CONFIRMATION_BODY_IS_ARRAY', Array.isArray(verified.body), true);
    observedCount = observed.body.length;
    verifiedCount = verified.body.length;
    observer.check(attempt, 'CONFIRMATION_ORDER_COUNT', verifiedCount, 1);
    observer.check(attempt, 'CONFIRMATION_ORDER_ID', verified.body[0]?.id ?? null, submitted.response.body.orderId);
    observer.check(attempt, 'HISTORY_ORDER_COUNT', observedCount, 1);
    observer.check(attempt, 'HISTORY_ORDER_ID', observed.body[0]?.id ?? null, submitted.response.body.orderId);
    observer.check(attempt, 'HISTORY_ORDER_OWNER', observed.body[0]?.user_id ?? null, user.id);
    observer.check(attempt, 'HISTORY_ORDER_TOTAL', observed.body[0]?.total_amount ?? null, product.price);
    observer.check(attempt, 'HISTORY_ORDER_STATUS', observed.body[0]?.status ?? null, 'pending');
  } catch (error) {
    failure = error;
  } finally {
    if (pendingSubmit) {
      const submitted = await pendingSubmit;
      if (submitted.error && !failure) failure = submitted.error;
    }
    if (harness) {
      try {
        await harness.close();
        observer.event(attempt, 'fixture.closed', { fixture_id: fixtureId });
      } catch (error) {
        const details = { category: 'cleanup', code: 'FIXTURE_CLOSE_ERROR', message: 'Fixture cleanup did not complete normally' };
        error.evidence = details;
        if (!failure) failure = error;
        else additionalFailure = details;
      }
    }
    const details = failure ? failure.evidence || {
      category: phase === 'setup' ? 'setup' : 'execution', code: 'UNEXPECTED_ERROR',
      message: `Unexpected error during ${phase}; inspect the original runner output`,
    } : null;
    // A setup assertion must not be counted as evidence of the intended flake.
    if (details && phase === 'setup') details.category = 'setup';
    const result = {
      test_id: 'ORDER-HISTORY-01', run_id: process.env.ORDER_RUN_ID || 'run-01', attempt,
      retry_of_attempt: attempt === 1 ? null : attempt - 1, fixture_id: fixtureId,
      status: failure ? 'failed' : 'passed',
      started_elapsed_ms: started.elapsed_ms,
      completed_elapsed_ms: observer.elapsed(),
      observed_order_count: observedCount, confirmation_order_count: verifiedCount,
      failure: details, additional_failure: additionalFailure,
    };
    observer.event(attempt, 'attempt.finished', { status: result.status, failure: details });
    observer.append('attempts', result);
  }
  if (failure) throw failure;
});
