import { ApiObject } from './api_object.js';

// Use this class to get and to print all of the available
// advertising delivery metrics.
export class DeliveryMetrics extends ApiObject {
  // Get the full list of all available delivery metrics.
  // This call is not used much in day-to-day API code, but is a useful endpoint
  // for learning about the metrics.
  // https://developers.pinterest.com/docs/api/v5/#operation/delivery_metrics/get
  async get() {
    return (await this.request_data('/v5/resources/delivery_metrics')).items;
  }

  summary(delivery_metric) {
    return `${delivery_metric.name}: ${delivery_metric.definition}`;
  }

  // Print summary of a single metric.
  print(delivery_metric) {
    console.log(this.summary(delivery_metric));
  }

  // Print summary of data returned by get().
  print_all(delivery_metrics) {
    console.log('Available delivery metrics:');
    for (const [idx, metric] of delivery_metrics.entries()) {
      console.log(`[${idx + 1}] ${this.summary(metric)}`);
    }
  }
}
