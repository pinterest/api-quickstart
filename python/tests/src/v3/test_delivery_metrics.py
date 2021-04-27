import unittest
import mock
from mock import call
import datetime
from src.v3.delivery_metrics import DeliveryMetrics
from src.v3.delivery_metrics import DeliveryMetricsAsyncReport

class DeliveryMetricsTest(unittest.TestCase):

    @mock.patch('builtins.print')
    @mock.patch('src.v3.user.ApiObject.request_data')
    @mock.patch('src.v3.delivery_metrics.ApiObject.__init__')
    def test_delivery_metrics(self, mock_api_object_init, mock_api_object_request_data, mock_print):
        test_dm = DeliveryMetrics('test_api_config', 'test_access_token')
        mock_api_object_init.assert_called_once_with('test_api_config', 'test_access_token')

        mock_api_object_request_data.return_value = {'metrics':
                                                     [{'name': 'metric1',
                                                       'definition': 'description 1'},
                                                      {'name': 'metric2',
                                                       'definition': 'description 2'}]
                                                     }
        metrics = test_dm.get()
        self.assertEqual(test_dm.summary(metrics[1]), 'metric2: description 2')
        test_dm.print_all(metrics)
        mock_print.assert_has_calls([call('Available delivery metrics:'),
                                     call('[1] metric1: description 1'),
                                     call('[2] metric2: description 2')
                                     ])
        
class DeliveryMetricsAsyncReportTest(unittest.TestCase):

    @mock.patch('src.v3.delivery_metrics.AsyncReport.__init__')
    def test_dm_async_report(self, mock_async_report_init):
        dm_async_report = DeliveryMetricsAsyncReport(
            'test_api_config', 'test_access_token', 'test_advertiser_id') \
            .start_date('2021-03-01') \
            .end_date('2021-03-31') \
            .level('PIN_PROMOTION') \
            .metrics({'IMPRESSION_1', 'CLICKTHROUGH_1'}) \
            .report_format('json')
            
        mock_async_report_init.assert_called_once_with(
            'test_api_config', 'test_access_token', 'test_advertiser_id')

        uri_attributes = dm_async_report.post_uri_attributes()
        self.assertEqual(uri_attributes,
                         '?start_date=2021-03-01&end_date=2021-03-31' +
                         '&metrics=CLICKTHROUGH_1,IMPRESSION_1&level=PIN_PROMOTION' +
                         '&report_format=json')

        dm_async_report.date_range('2021-03-31', '2021-03-01') # wrong order
        with self.assertRaisesRegex(ValueError, 'start date after end date'):
            dm_async_report.post_uri_attributes()

    @mock.patch('src.v3.delivery_metrics.datetime.date', wraps=datetime.date)
    @mock.patch('src.v3.delivery_metrics.AsyncReport.__init__')
    def test_dm_async_report_attributes(self, mock_async_report_init, mock_date):
        mock_date.today.return_value=datetime.datetime(2021, 3, 31) # for call to last_30_days below

        # These attributes might not actually make any sense, but they are
        # valid and test most of the attribute functions.
        dm_async_report = DeliveryMetricsAsyncReport(
            'test_api_config', 'test_access_token', 'test_advertiser_id') \
            .last_30_days() \
            .level('SEARCH_QUERY') \
            .click_window_days(14) \
            .conversion_report_time('AD_EVENT') \
            .data_source('REALTIME') \
            .engagement_window_days(7) \
            .granularity('HOUR') \
            .report_format('csv') \
            .tag_version(3) \
            .view_window_days(30)
        # specify metrics with multiple calls
        dm_async_report.metrics({'INAPP_SEARCH_ROAS', 'INAPP_SEARCH_COST_PER_ACTION'})
        dm_async_report.metric('TOTAL_CLICK_SEARCH_QUANTITY')
        dm_async_report.metric('TOTAL_CLICK_SEARCH')
        

        uri_attributes = dm_async_report.post_uri_attributes()
        self.assertEqual(uri_attributes,
                         '?start_date=2021-03-01&end_date=2021-03-31' +
                         '&metrics=INAPP_SEARCH_COST_PER_ACTION,INAPP_SEARCH_ROAS,' +
                         'TOTAL_CLICK_SEARCH,TOTAL_CLICK_SEARCH_QUANTITY' +
                         '&level=SEARCH_QUERY' + 
                         '&click_window_days=14' +
                         '&conversion_report_time=AD_EVENT' +
                         '&data_source=REALTIME' +
                         '&engagement_window_days=7' +
                         '&granularity=HOUR' +
                         '&report_format=csv' +
                         '&tag_version=3' +
                         '&view_window_days=30')

    @mock.patch('src.v3.delivery_metrics.AsyncReport.__init__')
    def test_dm_async_report_attributes(self, mock_async_report_init):
        dm_async_report = DeliveryMetricsAsyncReport(
            'test_api_config', 'test_access_token', 'test_advertiser_id') \
            .date_range('2021-03-01', '2021-03-31') \
            .level('oops') \
            .metrics({'IMPRESSION_1', 'CLICKTHROUGH_1'})

        with self.assertRaisesRegex(ValueError, 'level: oops is not one of'):
            dm_async_report.post_uri_attributes()

        dm_async_report.level('KEYWORD')
        dm_async_report.tag_version(4)

        with self.assertRaisesRegex(ValueError, 'tag_version: 4 is not one of'):
            dm_async_report.post_uri_attributes()
