import { AdMetricsAsyncReport } from './ad_metrics_async_report.js';
import { AsyncReport } from '../async_report.js';

jest.mock('../async_report');

describe('ad_metrics_async_report tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  // Just need to test that the version-specific report initializes
  // the contained AsyncReport with the appropriate path.
  test('ad metrics async report', async() => {
    const ad_async_report = new AdMetricsAsyncReport(
      'test_api_config', 'test_access_token', 'test_advertiser_id'
    );

    expect(ad_async_report).toBeInstanceOf(AdMetricsAsyncReport);
    expect(AsyncReport.mock.instances.length).toBe(1);
    expect(AsyncReport.mock.calls[0]).toEqual([
      'test_api_config',
      'test_access_token',
      '/v5/ad_accounts/test_advertiser_id/reports'
    ]);
  });
});
