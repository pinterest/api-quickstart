import { AdMetricsAsyncReportCommon } from './ad_metrics_async_report_common.js';

describe('ad_metrics_async_report_common tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('ad async report attributes', async() => {
    const ad_async_report = new AdMetricsAsyncReportCommon()
      .start_date('2021-03-01')
      .end_date('2021-03-31')
      .level('PIN_PROMOTION')
      .metrics(['IMPRESSION_1', 'CLICKTHROUGH_1'])
      .report_format('JSON');

    expect(() => {
      ad_async_report.post_data_attributes();
    }).toThrowError(
      new Error('missing attributes: granularity')
    );

    ad_async_report.granularity('DAY');

    expect(ad_async_report.post_data_attributes())
      .toEqual({
        start_date: '2021-03-01',
        end_date: '2021-03-31',
        columns: ['CLICKTHROUGH_1', 'IMPRESSION_1'],
        level: 'PIN_PROMOTION',
        granularity: 'DAY',
        report_format: 'JSON'
      });

    ad_async_report.date_range('2021-03-31', '2021-03-01'); // wrong order
    expect(() => {
      ad_async_report.post_data_attributes();
    }).toThrowError(
      new Error('start date after end date')
    );
  });

  test('ad metrics async report attribute errors', async() => {
    const ad_async_report = new AdMetricsAsyncReportCommon()
      .date_range('2021-03-01', '2021-03-31')
      .granularity('DAY')
      .level('oops')
      .metrics(['IMPRESSION_1', 'CLICKTHROUGH_1']);

    expect(() => {
      ad_async_report.post_data_attributes();
    }).toThrowError(
      new Error('\
level: oops is not one of ADVERTISER,AD_GROUP,CAMPAIGN,ITEM,\
KEYWORD,PIN_PROMOTION,PIN_PROMOTION_TARGETING,PRODUCT_GROUP,\
PRODUCT_GROUP_TARGETING,PRODUCT_ITEM,SEARCH_QUERY')
    );

    ad_async_report.level('KEYWORD');
    ad_async_report.report_format('json');
    expect(() => {
      ad_async_report.post_data_attributes();
    }).toThrowError(
      new Error('report_format: json is not one of CSV,JSON')
    );

    ad_async_report.report_format('CSV');
    ad_async_report.tag_version(4);

    expect(() => {
      ad_async_report.post_data_attributes();
    }).toThrowError(
      new Error('tag_version: 4 is not one of 2,3,2,3')
    );
  });
});
