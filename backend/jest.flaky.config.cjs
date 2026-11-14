// Explicit opt-in: the experiment never matches the normal *.test.js suite.
module.exports = {
  ...require('./jest.config.cjs'),
  testMatch: ['<rootDir>/tests/experiments/order-history.case.js'],
  collectCoverage: false,
};
