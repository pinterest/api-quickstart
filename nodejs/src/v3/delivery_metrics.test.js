import { ApiObject } from '../api_object.js';
import { AsyncReport } from './async_report.js';
import { DeliveryMetrics, DeliveryMetricsAsyncReport } from './delivery_metrics.js';

jest.mock('../api_object');
jest.mock('./async_report');

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
      metrics: [
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

  test('delivery metrics async report attributes', async() => {
    const dm_async_report = new DeliveryMetricsAsyncReport(
      'test_api_config', 'test_access_token', 'test_advertiser_id')
      .start_date('2021-03-01')
      .end_date('2021-03-31')
      .level('PIN_PROMOTION')
      .metrics(['IMPRESSION_1', 'CLICKTHROUGH_1'])
      .report_format('json');

    expect(AsyncReport.mock.instances.length).toBe(1);
    expect(AsyncReport.mock.calls[0]).toEqual([
      'delivery_metrics', 'test_api_config', 'test_access_token', 'test_advertiser_id'
    ]);

    expect(dm_async_report.post_uri_attributes())
      .toEqual('\
start_date=2021-03-01&end_date=2021-03-31\
&metrics=CLICKTHROUGH_1,IMPRESSION_1&level=PIN_PROMOTION\
&report_format=json');

    dm_async_report.date_range('2021-03-31', '2021-03-01'); // wrong order
    expect(() => {
      dm_async_report.post_uri_attributes();
    }).toThrowError(
      new Error('start date after end date')
    );
  });

  test('delivery metrics async report run', async() => {
    jest.spyOn(global.Date, 'now')
      .mockImplementationOnce(() =>
        new Date('2021-05-31T09:22:43.762Z').valueOf()
      ); // for call to last_30_days

    // These attributes might not actually make any sense, but they are
    // valid and test most of the attribute functions.
    const dm_async_report = new DeliveryMetricsAsyncReport(
      'test_api_config', 'test_access_token', 'test_advertiser_id')
      .last_30_days()
      .level('SEARCH_QUERY')
      .click_window_days(14)
      .conversion_report_time('AD_EVENT')
      .data_source('REALTIME')
      .engagement_window_days(7)
      .granularity('HOUR')
      .report_format('csv')
      .tag_version(3)
      .view_window_days(30);

    // specify metrics with multiple calls
    dm_async_report.metrics(['INAPP_SEARCH_ROAS', 'INAPP_SEARCH_COST_PER_ACTION']);
    dm_async_report.metric('TOTAL_CLICK_SEARCH_QUANTITY');
    dm_async_report.metric('TOTAL_CLICK_SEARCH');

    const mock_run = jest.spyOn(AsyncReport.prototype, 'run');
    dm_async_report.run();

    expect(mock_run.mock.calls).toEqual([['\
start_date=2021-05-01&end_date=2021-05-31\
&metrics=INAPP_SEARCH_COST_PER_ACTION,INAPP_SEARCH_ROAS,\
TOTAL_CLICK_SEARCH,TOTAL_CLICK_SEARCH_QUANTITY\
&click_window_days=14\
&conversion_report_time=AD_EVENT\
&data_source=REALTIME\
&engagement_window_days=7\
&granularity=HOUR\
&level=SEARCH_QUERY\
&report_format=csv\
&tag_version=3\
&view_window_days=30']]);
  });

  test('delivery metrics async report attribute errors', async() => {
    const dm_async_report = new DeliveryMetricsAsyncReport(
      'test_api_config', 'test_access_token', 'test_advertiser_id')
      .date_range('2021-03-01', '2021-03-31')
      .level('oops')
      .metrics(['IMPRESSION_1', 'CLICKTHROUGH_1']);

    expect(() => {
      dm_async_report.post_uri_attributes();
    }).toThrowError(
      new Error('\
level: oops is not one of ADVERTISER,AD_GROUP,CAMPAIGN,ITEM,\
KEYWORD,PIN_PROMOTION,PIN_PROMOTION_TARGETING,PRODUCT_GROUP,\
PRODUCT_GROUP_TARGETING,PRODUCT_ITEM,SEARCH_QUERY')
    );

    dm_async_report.level('KEYWORD');
    dm_async_report.tag_version(4);

    expect(() => {
      dm_async_report.post_uri_attributes();
    }).toThrowError(
      new Error('tag_version: 4 is not one of 2,3,2,3')
    );
  });
});
