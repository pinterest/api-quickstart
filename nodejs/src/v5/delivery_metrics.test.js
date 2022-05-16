import { DeliveryMetrics } from './delivery_metrics.js';

describe('delivery_metrics tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('delivery metrics', async() => {
    const test_dm = new DeliveryMetrics();

    await expect(async() => {
      await test_dm.get();
    }).rejects.toThrowError(
      new Error('Metric definitions are not available in API version v5.')
    );
  });
});
