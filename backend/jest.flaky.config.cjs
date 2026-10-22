// Explicit opt-in: *.flaky.js does not match the normal *.test.js suite.
module.exports = {
  ...require('./jest.config.cjs'),
  testMatch: ['<rootDir>/tests/experiments/**/*.flaky.js'],
  collectCoverage: false,
};
