import { ApiObject } from '../api_object.js';
import { AsyncReport } from './async_report.js';

jest.mock('../api_object');
const api_object_actual = jest.requireActual('../api_object');

describe('async report tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v3 async report methods', async() => {
    const mock_constructor = jest.spyOn(ApiObject.prototype, 'constructor');
    const test_report1 = new AsyncReport(
      'test_report1', 'test_api_config', 'test_access_token', 'test_advertiser_id'
    );
    expect(mock_constructor.mock.calls).toEqual([['test_api_config', 'test_access_token']]);
    const mock_post_data = jest.spyOn(ApiObject.prototype, 'post_data');
    mock_post_data.mockResolvedValueOnce({ token: 'test_report1_token' });
    await test_report1.request_report('test_report1_attributes');

    expect(test_report1.token).toEqual('test_report1_token');
    expect(mock_post_data.mock.calls).toEqual([['\
/ads/v3/reports/async/test_advertiser_id/test_report1/\
?test_report1_attributes']]);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValueOnce({
      report_status: 'FINISHED',
      url: 'test_report1_url'
    });
    await test_report1.wait_report();
    expect(test_report1.url()).toEqual('test_report1_url');
    expect(mock_request_data.mock.calls).toEqual([['\
/ads/v3/reports/async/test_advertiser_id/test_report1/\
?token=test_report1_token']]);
  });

  test('v3 async report run', async() => {
    const test_report2_url = '\
test_report2_url/x-y-z/metrics_report.txt?Very-long-credentials-string';

    const test_report2 = new AsyncReport(
      'test_report2', 'test_api_config', 'test_access_token', 'test_advertiser_id'
    );

    const mock_post_data = jest.spyOn(ApiObject.prototype, 'post_data');
    mock_post_data.mockResolvedValueOnce({ token: 'test_report2_token' });

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data // simulate time required to generate the test
      .mockResolvedValueOnce({ report_status: 'IN_PROGRESS' })
      .mockResolvedValueOnce({ report_status: 'IN_PROGRESS' })
      .mockResolvedValueOnce({ report_status: 'IN_PROGRESS' })
      .mockResolvedValueOnce({ report_status: 'IN_PROGRESS' })
      .mockResolvedValueOnce({ report_status: 'IN_PROGRESS' })
      .mockResolvedValueOnce({ report_status: 'IN_PROGRESS' })
      .mockResolvedValueOnce(
        { report_status: 'FINISHED', url: test_report2_url });

    console.log = jest.fn(); // test output

    // Return from setTimeout immediately, saving the requested timeout.
    // Note: jest.useFakeTimers() is hard to use with async functions,
    //       so this test uses a more basic approach.
    const mock_set_timeout = jest.spyOn(global, 'setTimeout');
    const timeout_calls = [];
    mock_set_timeout.mockImplementation((callback, timeout) => {
      timeout_calls.push(timeout); // save the requested timeout
      callback(); // run the timer callback immediately
    });

    // unmock the backoff functions
    const api_object = new api_object_actual.ApiObject('test1', 'test2');
    jest.spyOn(ApiObject.prototype, 'reset_backoff')
      .mockImplementation(api_object.reset_backoff);
    jest.spyOn(ApiObject.prototype, 'wait_backoff')
      .mockImplementation(api_object.wait_backoff);

    await test_report2.run('test_report2_attributes');

    // verify that the backoff algorithm is working as expected
    expect(timeout_calls).toEqual([
      1000, 2000, 4000, 8000, 10000, 10000
    ]);

    // verify that the printout works
    expect(console.log.mock.calls).toEqual([
      ['Report status: IN_PROGRESS. Waiting a second...'],
      ['Report status: IN_PROGRESS. Waiting 2 seconds...'],
      ['Report status: IN_PROGRESS. Waiting 4 seconds...'],
      ['Report status: IN_PROGRESS. Waiting 8 seconds...'],
      ['Report status: IN_PROGRESS. Waiting 10 seconds...'],
      ['Report status: IN_PROGRESS. Waiting 10 seconds...']
    ]);

    expect(test_report2.url()).toEqual(test_report2_url); // verify returned URL
    // verify API requests
    expect(mock_post_data.mock.calls).toEqual([['\
/ads/v3/reports/async/test_advertiser_id/test_report2/\
?test_report2_attributes']]);
    // request data will be called multiple times
    expect(mock_request_data).toHaveBeenCalledWith('\
/ads/v3/reports/async/test_advertiser_id/test_report2/\
?token=test_report2_token');

    // verify filename
    expect(test_report2.filename()).toEqual('metrics_report.txt');
  });
});
