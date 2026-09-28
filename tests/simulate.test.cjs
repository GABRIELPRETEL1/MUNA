const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

// Load the same financial engine used by the standalone browser page.
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const engine = script.slice(script.indexOf('function teaFromNominal'), script.indexOf('function renderTable'));
const { simulate, scenarioSet } = vm.runInNewContext(engine + '; ({ simulate, scenarioSet })');

const inputs = {
  principal: 0, monthly: 0, rate: 0.12, years: 1, freq: 12,
  inflation: 0, tax: 0, fee: 0, target: 0, contribGrowth: 0
};
const near = (actual, expected) => assert.ok(
  Math.abs(actual - expected) < 1e-8,
  `expected ${expected}, received ${actual}`
);

test('principal without deposits follows the selected compounding frequency', () => {
  for (const freq of [1, 2, 4, 12, 365]) {
    const result = simulate({ ...inputs, principal: 1000, freq, years: 2 });
    near(result.final.balance, 1000 * (1 + inputs.rate / freq) ** (2 * freq));
    near(result.final.totalContrib, 1000);
    near(result.final.gainAcc, result.final.balance - 1000);
  }
});

test('twelve end-of-month deposits earn interest within the contribution year', () => {
  const result = simulate({ ...inputs, monthly: 100, target: 1260 });
  const expected = 100 * ((1.01 ** 12 - 1) / 0.01);
  near(result.final.balance, expected);
  near(result.final.preTaxGain, expected - 1200);
  near(result.final.annualContribution, 1200);
  near(result.final.totalContrib, 1200);
  assert.equal(result.reachedAt, 1);
});

test('fees, tax, inflation, and annual deposit growth reconcile with annual rows', () => {
  const options = {
    ...inputs, principal: 500, monthly: 100, years: 2, freq: 4,
    fee: 0.02, tax: 0.25, inflation: 0.03, contribGrowth: 0.10, target: 10000
  };
  const monthlyRate = (1 + (options.rate - options.fee) / 4) ** (4 / 12) - 1;
  let balance = options.principal;
  let contributed = options.principal;
  const result = simulate(options);
  for (let year = 1; year <= 2; year++) {
    const contribution = 100 * 1.1 ** (year - 1);
    const start = balance;
    for (let month = 0; month < 12; month++) {
      balance = balance * (1 + monthlyRate) + contribution;
    }
    const gross = balance - start - 12 * contribution;
    const taxPaid = gross * options.tax;
    balance -= taxPaid;
    contributed += 12 * contribution;
    const row = result.rows[year - 1];
    near(row.preTaxGain, gross);
    near(row.taxPaid, taxPaid);
    near(row.netGain, gross - taxPaid);
    near(row.annualContribution, contribution * 12);
    near(row.balance, balance);
    near(row.totalContrib, contributed);
    near(row.realBalance, balance / 1.03 ** year);
    near(row.gainAcc, balance - contributed);
  }
  assert.equal(result.reachedAt, null);
  const scenarios = scenarioSet(options);
  near(scenarios.base.final.balance, result.final.balance);
  assert.ok(scenarios.pesimista.final.balance < result.final.balance);
  assert.ok(scenarios.optimista.final.balance > result.final.balance);
});
