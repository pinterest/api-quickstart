// Jest required Babel to handle the modern module structure used by this nodejs code.
// This file has the standard, minimal configuration for using Babel with Jest.
// For this configuration to work, Need to run: npm install --save-dev @babel/preset-env
module.exports = {
  presets: [['@babel/preset-env', {targets: {node: 'current'}}]],
};
