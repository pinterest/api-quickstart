/**
 * This module will provide access to delivery metrics when it becomes available.
 */

// Use this class to get and to print all of the available
// advertising delivery metrics.
//   https://developers.pinterest.com/docs/api/v5/#operation/delivery_metrics/get
export class DeliveryMetrics {
  // The full list of all available delivery metrics will be available in v5 soon.
  async get() {
    throw new Error('Metric definitions are not available in API version v5.');
  }
}
