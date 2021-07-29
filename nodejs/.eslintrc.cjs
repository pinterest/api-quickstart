module.exports = {
  env: {
    browser: true,
    es2021: true,
    'jest/globals': true
  },
  extends: [
    'plugin:jest/recommended',
    'standard'
  ],
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module'
  },
  plugins: [
    'jest'
  ],
  rules: {
    camelcase: 'off', // makes it easier to keep python and nodejs code in sync
    'jest/no-disabled-tests': 'error', // prefer error to warning
    'no-extra-parens': ['error', 'all'], // additional code simplification
    semi: ['error', 'always'], // prefer C-style semicolons
    'space-before-function-paren': ['error', 'never'] // prefer C-style functions
  }
};
