import { UserAnalytics, PinAnalytics, AdAnalytics } from './analytics.js';
import { ApiObject } from '../api_object.js';

jest.mock('../api_object');

describe('v5 analytics tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v5 user analytics', async() => {
    const analytics = new UserAnalytics(
      'test_user_id', 'test_api_config', 'test_access_token')
      .start_date('2021-03-01')
      .end_date('2021-03-31')
      .metrics(['PIN_CLICK_RATE', 'IMPRESSION'])
      .pin_format('regular')
      .from_claimed_content('Both');

    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(
      ['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    expect(await analytics.get('test_ad_account'))
      .toEqual('test_response');

    // note that metrics should be sorted
    expect(mock_request_data.mock.calls[0][0])
      .toEqual('\
/v5/user_account/analytics?\
start_date=2021-03-01&end_date=2021-03-31\
&metric_types=IMPRESSION,PIN_CLICK_RATE\
&ad_account_id=test_ad_account\
&from_claimed_content=Both&pin_format=regular');

    // add a couple of fields
    analytics.app_types('web').split_field('PIN_FORMAT');

    // verifies additional parameters and no ad_account_id
    expect(await analytics.get(null)).toEqual('test_response');
    expect(mock_request_data.mock.calls[1][0])
      .toEqual('\
/v5/user_account/analytics?\
start_date=2021-03-01&end_date=2021-03-31\
&metric_types=IMPRESSION,PIN_CLICK_RATE\
&app_types=web\
&from_claimed_content=Both&pin_format=regular\
&split_field=PIN_FORMAT');
  });

  test('v5 pin analytics', async() => {
    const analytics = new PinAnalytics(
      'test_pin_id', 'test_api_config', 'test_access_token')
      .start_date('2021-03-01')
      .end_date('2021-03-31')
      .metrics(['PIN_CLICK', 'IMPRESSION']);

    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(
      ['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    expect(await analytics.get('test_ad_account'))
      .toEqual('test_response');

    // note that metrics should be sorted
    expect(mock_request_data.mock.calls[0][0])
      .toEqual('\
/v5/pins/test_pin_id/analytics?\
start_date=2021-03-01&end_date=2021-03-31\
&metric_types=IMPRESSION,PIN_CLICK\
&ad_account_id=test_ad_account');

    analytics.app_types('WEB');
    analytics.split_field('NO_SPLIT');

    // verifies additional parameters and no ad_account_id
    expect(await analytics.get(null)).toEqual('test_response');
    expect(mock_request_data.mock.calls[1][0])
      .toEqual('\
/v5/pins/test_pin_id/analytics?\
start_date=2021-03-01&end_date=2021-03-31\
&metric_types=IMPRESSION,PIN_CLICK\
&app_types=WEB&split_field=NO_SPLIT');
  });

  test('v5 ads analytics', async() => {
    const analytics = new AdAnalytics('test_api_config', 'test_access_token')
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
/v5/ad_accounts/test_ad_account/analytics?\
start_date=2021-03-01&end_date=2021-03-31\
&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH\
&granularity=DAY');

    analytics.click_window_days(7);
    expect(await analytics.get_campaign('test_ad_account', 'test_campaign'))
      .toEqual('test_response');
    expect(mock_request_data.mock.calls[1][0])
      .toEqual('\
/v5/ad_accounts/test_ad_account/campaigns/analytics?\
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
/v5/ad_accounts/test_ad_account/ad_groups/analytics?\
ad_group_ids=test_ad_group\
&start_date=2021-03-01&end_date=2021-03-31\
&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH\
&click_window_days=7\
&engagement_window_days=14\
&granularity=HOUR');

    analytics.view_window_days(60).conversion_report_time('TIME_OF_CONVERSION');
    expect(await analytics.get_ad(
      'test_ad_account', 'test_campaign', 'test_ad_group', 'test_ad'))
      .toEqual('test_response');
    expect(mock_request_data.mock.calls[3][0])
      .toEqual('\
/v5/ad_accounts/test_ad_account/ads/analytics?\
ad_ids=test_ad\
&start_date=2021-03-01&end_date=2021-03-31\
&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH\
&click_window_days=7\
&conversion_report_time=TIME_OF_CONVERSION\
&engagement_window_days=14\
&granularity=HOUR\
&view_window_days=60');
  });
});
