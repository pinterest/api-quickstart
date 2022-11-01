import { ApiObject } from './api_object.js';
import { DeliveryMetrics } from './delivery_metrics.js';

jest.mock('./api_object');

describe('delivery_metrics tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('delivery metrics', async() => {
    const test_dm = new DeliveryMetrics('test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValueOnce({
      items: [
        { name: 'metric1', definition: 'description 1' },
        { name: 'metric2', definition: 'description 2' }
      ]
    });
    const metrics = await test_dm.get();

    expect(test_dm.summary(metrics[1])).toEqual('metric2: description 2');

    console.log = jest.fn(); // test output
    test_dm.print_all(metrics);
    expect(console.log.mock.calls).toEqual([
      ['Available delivery metrics:'],
      ['[1] metric1: description 1'],
      ['[2] metric2: description 2']
    ]);
  });
});
