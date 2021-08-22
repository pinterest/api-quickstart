import { Analytics, AdAnalytics } from './analytics.js';
import { ApiObject } from '../api_object.js';

jest.mock('../api_object');

describe('v3 analytics tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v3 analytics', async() => {
    const analytics = new Analytics(
      'test_user_id', 'test_api_config', 'test_access_token')
      .start_date('2021-03-01')
      .end_date('2021-03-31')
      .metrics(['PIN_CLICK_RATE', 'IMPRESSION'])
      .pin_format('standard')
      .from_owned_content(1);

    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(
      ['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    console.log = jest.fn(); // test output

    expect(await analytics.get('ad_account_id')).toEqual(null);
    expect(console.log.mock.calls).toEqual([
      ['User account analytics for shared accounts are'],
      ['supported by Pinterest API v5, but not v3 or v4.']
    ]);

    expect(await analytics.get(null)).toEqual('test_response');

    // note that metrics should be sorted
    expect(mock_request_data.mock.calls[0][0])
      .toEqual('\
/v3/partners/analytics/users/test_user_id/metrics/?\
start_date=2021-03-01&end_date=2021-03-31\
&metric_types=IMPRESSION,PIN_CLICK_RATE\
&from_owned_content=1&pin_format=standard');

    // test the other attributes
    analytics
      .paid(2)
      .in_profile(0)
      .downstream(2)
      .app_types('tablet')
      .publish_types('all')
      .include_curated(1);

    // verifies additional parameters and no ad_account_id
    expect(await analytics.get(null)).toEqual('test_response');
    expect(mock_request_data.mock.calls[1][0])
      .toEqual('\
/v3/partners/analytics/users/test_user_id/metrics/?\
start_date=2021-03-01&end_date=2021-03-31\
&metric_types=IMPRESSION,PIN_CLICK_RATE\
&app_types=tablet&downstream=2\
&from_owned_content=1\
&in_profile=0&include_curated=1&paid=2\
&pin_format=standard&publish_types=all');
  });

  test('v4 ads analytics', async() => {
    const analytics = new AdAnalytics(
      'test_user_id', 'test_api_config', 'test_access_token')
      .start_date('2021-03-01')
      .end_date('2021-03-31');

    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(
      ['test_api_config', 'test_access_token']);

    await expect(async() => {
      await analytics.get_ad_account('should_not_be_used');
    }).rejects.toThrowError(
      new Error('missing attributes: granularity')
    );

    analytics.granularity('DAY');
    await expect(async() => {
      await analytics.get_ad_account('should_not_be_used');
    }).rejects.toThrowError(
      new Error('metrics not set')
    );

    analytics.metrics(['TOTAL_CLICKTHROUGH', 'SPEND_IN_DOLLAR']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    expect(await analytics.get_ad_account('test_ad_account'))
      .toEqual('test_response');
    // note that metrics should be sorted
    expect(mock_request_data.mock.calls[0][0])
      .toEqual('\
/ads/v4/advertisers/test_ad_account/delivery_metrics?\
start_date=2021-03-01&end_date=2021-03-31\
&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH\
&granularity=DAY');

    analytics.click_window_days(7);
    expect(await analytics.get_campaign('test_ad_account', 'test_campaign'))
      .toEqual('test_response');
    expect(mock_request_data.mock.calls[1][0])
      .toEqual('\
/ads/v4/advertisers/test_ad_account/campaigns/delivery_metrics?\
campaign_ids=test_campaign\
&start_date=2021-03-01&end_date=2021-03-31\
&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH\
&click_window_days=7\
&granularity=DAY');

    analytics.engagement_window_days(14).granularity('HOUR');
    expect(await analytics.get_ad_group(
      'test_ad_account', 'test_campaign', 'test_ad_group'))
      .toEqual('test_response');
    expect(mock_request_data.mock.calls[2][0])
      .toEqual('\
/ads/v4/advertisers/test_ad_account/ad_groups/delivery_metrics?\
ad_group_ids=test_ad_group\
&start_date=2021-03-01&end_date=2021-03-31\
&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH\
&click_window_days=7\
&engagement_window_days=14\
&granularity=HOUR');

    analytics
      .view_window_days(60)
      .conversion_report_time('AD_EVENT')
      .attribution_types('HOUSEHOLD');
    expect(await analytics.get_ad(
      'test_ad_account', 'test_campaign', 'test_ad_group', 'test_ad'))
      .toEqual('test_response');
    expect(mock_request_data.mock.calls[3][0])
      .toEqual('\
/ads/v4/advertisers/test_ad_account/ads/delivery_metrics?\
ad_ids=test_ad\
&start_date=2021-03-01&end_date=2021-03-31\
&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH\
&attribution_types=HOUSEHOLD\
&click_window_days=7\
&conversion_report_time=AD_EVENT\
&engagement_window_days=14\
&granularity=HOUR\
&view_window_days=60');
  });
});
