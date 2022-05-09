/**
 * This module provides a compatible interface for an endpoint
 * that exists in v3 but not v5.
 */

// Use this class to get and to print all of the available
// advertising delivery metrics.
export class DeliveryMetrics {
  // No constructor is required, because the parent constructor
  // should be called automagically. See:
  //   https://eslint.org/docs/rules/no-useless-constructor

  // The full list of all available delivery metrics is available in v3 but not v5.
  async get() {
    throw new Error('Metric definitions are not available in API version v5.');
  }
}
