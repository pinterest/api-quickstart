import datetime

from api_object import ApiObject
from async_report import AsyncReport

class DeliveryMetrics(ApiObject):
    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)

    def get(self):
        """
        Get the available metrics.
        """
        return self.request_data('/ads/v3/resources/delivery_metrics/').get('metrics')

    def summary(self, delivery_metric):
        return f"{delivery_metric['name']}: {delivery_metric['definition']}"

    def print(self, delivery_metric):
        """
        Print summary of a single metric.
        """
        print(self.summary(delivery_metric))

    def print_all(self, delivery_metrics):
        """
        Print summary of data returned by get().
        """
        print('Available delivery metrics:')
        for idx, metric in enumerate(delivery_metrics):
            print(f"[{idx + 1}] " + self.summary(metric))

class DeliveryMetricsAsyncReport(AsyncReport):
    """
    Specifies all of the attributes for the async advertiser
    delivery metrics report. For more information, see:
    https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_create_advertiser_delivery_metrics_report_POST

    The attribute functions are chainable. For example:
    report = DeliveryMetricsAsyncReport(api_config, access_token, advertiser_id) \
             .start_date('2021-03-01') \
             .end_date('2021-03-31') \
             .level('PIN_PROMOTION') \
             .metrics({'IMPRESSION_1', 'CLICKTHROUGH_1'}) \
             .report_format('csv')
    """
    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(api_config, access_token, advertiser_id)
        self.kind_of = 'delivery_metrics' # override required by superclass
        self._start_date = None
        self._end_data = None
        self._metrics = set()
        self.attrs = {}

    # This dictionary lists values for attributes that are enumerated
    # in the API documentation. The keys are the names of the attributes,
    # and the dictionary values are sets of API-defined values.
    ENUMERATED_WINDOW_DAYS = {0, 1, 7, 14, 30, 60}
    ENUMERATED_VALUES = {
        'click_window_days': ENUMERATED_WINDOW_DAYS,
        'conversion_report_time': {'AD_EVENT','CONVERSION_EVENT'},
        'data_source': {'OFFLINE','REALTIME'},
        'engagement_window_days': ENUMERATED_WINDOW_DAYS,
        'entity_fields': {'AD_GROUP_ID','AD_GROUP_NAME','AD_GROUP_STATUS',
                          'CAMPAIGN_ID','CAMPAIGN_MANAGED_STATUS','CAMPAIGN_NAME',
                          'CAMPAIGN_STATUS','PIN_PROMOTION_ID','PIN_PROMOTION_NAME',
                          'PIN_PROMOTION_STATUS','PRODUCT_GROUP_ID'},
        'granularity': {'TOTAL','DAY','HOUR','WEEK','MONTH'},
        'level': {'ADVERTISER','AD_GROUP','CAMPAIGN', 'ITEM','KEYWORD','PIN_PROMOTION',
                  'PIN_PROMOTION_TARGETING','PRODUCT_GROUP','PRODUCT_GROUP_TARGETING',
                  'PRODUCT_ITEM','SEARCH_QUERY'},
        'report_format': {'csv','json'},
        'tag_version': {2, 3, '2', '3'},
        'view_window_days': ENUMERATED_WINDOW_DAYS
    }

    def check_enumerated_attr(self, name, value):
        """
        Check that the value of an enumerated attribute is an expected value.
        """
        values = self.ENUMERATED_VALUES[name]
        if value not in values:
            raise ValueError(f'{name}: {value} is not one of {values}')

    def check_enumerated_attrs(self):
        """
        Check the values of all of the enumerated attributes that have been
        set with their expected values.
        """
        for attr, value in self.attrs.items():
            self.check_enumerated_attr(attr, value)

    ATTR_DATE_FORMAT = '%Y-%m-%d'
    def check_date_attr(self, name, date):
        try:
            datetime.datetime.strptime(date, self.ATTR_DATE_FORMAT)
        except ValueError:
            raise ValueError(f'{name}: {date} needs to be a UTC date in YYYY-MM-DD format')

    def start_date(self, start_date):
        """
        Required attribute. Report start date (UTC): YYYY-MM-DD.
        """
        self._start_date = start_date
        return self

    def end_date(self, end_date):
        """
        Required attribute. Report end date (UTC): YYYY-MM-DD.
        """
        self._end_date = end_date
        return self

    def date_range(self, start_date, end_date):
        """
        Shortcut: set required start date and end date in one call.
        """
        self._start_date = start_date
        self._end_date = end_date
        return self

    def last_30_days(self):
        """
        Shortcut: set the end date to the current date and the start date
        to third days earlier.
        """
        today = datetime.date.today()
        today_minus_30 = today - datetime.timedelta(days=30)
        self.date_range(today_minus_30.strftime(self.ATTR_DATE_FORMAT),
                        today.strftime(self.ATTR_DATE_FORMAT))
        return self

    def level(self, level):
        """
        Required attribute. Requested report type.
        """
        self.attrs['level'] = level
        return self

    def metrics(self, metrics):
        """
        Not required, but strongly advised. May be set to 'ALL'.
        """
        self._metrics |= metrics # union with new metrics
        return self

    def metric(self, metric):
        """
        Adds a single metric to the metric set.
        """
        self._metrics.add(metric)
        return self

    # optional attributes...
    def click_window_days(self, click_window_days):
        """
        Number of days to use as the conversion attribution window for a 'click' action.
        Applies to Pinterest Tag conversion metrics. Prior conversion tags use their
        defined attribution windows. If not specified, defaults to 30 days.
        """
        self.attrs['click_window_days'] = click_window_days
        return self

    def conversion_report_time(self, conversion_report_time):
        """
        The date by which the conversion metrics returned from this endpoint will be reported.
        There are two dates associated with a conversion event: the date that the user interacted
        with the ad, and the date that the user completed a conversion event.
        """
        self.attrs['conversion_report_time'] = conversion_report_time
        return self

    def data_source(self, data_source):
        """
        Either OFFLINE or REALTIME. Offline metrics have a long retention and are used for
        billing (source of truth). Realtime metrics have latest metrics (including today)
        but only have a 72-hour retention. In addition, realtime metrics are expected to be
        an estimation and could be slightly inaccurate. Please note that only a limited set
        of metrics are available for realtime data.
        """
        self.attrs['data_source'] = data_source
        return self

    def engagement_window_days(self, engagement_window_days):
        """
        Number of days to use as the conversion attribution window for an engagement action.
        Engagements include saves, pin clicks, and carousel card swipes. Applies to
        Pinterest Tag conversion metrics. Prior conversion tags use their defined attribution
        windows. If not specified, defaults to 30 days.
        """
        self.attrs['engagement_window_days'] = engagement_window_days
        return self

    def entity_fields(self, entity_fields):
        """
        Additional fields that you would like included for each entity in the Delivery Metrics Report.
        Fields will be prefixed with the requested level when returned in the report, for example if
        CAMPAIGN_ID is requested at the AD_GROUP level, this field will be called AD_GROUP_CAMPAIGN_ID.
        Please note that entity fields can only be requested for the specified level and its parents,
        for example, for an AD_GROUP level request CAMPAIGN and AD_GROUP entity_fields can be requested,
        but PIN_PROMOTION entity_fields cannot.
        """
        self.attrs['entity_fields'] = entity_fields
        return self

    def granularity(self, granularity):
        """
        TOTAL - metrics are aggregated over the specified date range.
        DAY - metrics are broken down daily.
        HOUR - metrics are broken down hourly.
        WEEK - metrics are broken down weekly.
        MONTH - metrics are broken down monthly.
        Currently, we only support hourly breakdown when data_source=REALTIME.
        """
        self.attrs['granularity'] = granularity
        return self

    def filters(self, filters):
        raise 'TODO: not sure how filters need to be encoded'
        self.attrs['filters'] = filters
        return self

    def report_format(self, report_format):
        """
        Specification for formatting report data.
        """
        self.attrs['report_format'] = report_format
        return self

    def tag_version(self, tag_version):
        """
        By default, Pinterest Tag metrics are returned. To view metrics from prior conversion tags, set this field to 2.
        """
        self.attrs['tag_version'] = tag_version
        return self

    def view_window_days(self, view_window_days):
        """
        Number of days to use as the conversion attribution window for a view action.
        Applies to Pinterest Tag conversion metrics. Prior conversion tags use their
        defined attribution windows. If not specified, defaults to 1 day.
        """
        self.attrs['view_window_days'] = view_window_days
        return self

    def verify_attributes(self):
        # check the required start and end date attributes
        if not self._start_date:
            raise AttributeError('start date not set')
        self.check_date_attr('start_date', self._start_date)
        if not self._end_date:
            raise AttributeError('end date not set')
        self.check_date_attr('end_date', self._end_date)
        if not self._start_date <= self._end_date:
            raise ValueError('start date after end date')

        # check the other two required attributes
        if not self._metrics:
            raise AttributeError('metrics not set')
        if not self.attrs.get('level'):
            raise AttributeError('level not set')

        # check all of the attributes with enumerated values
        self.check_enumerated_attrs()

    def post_uri_attributes(self):
        """
        This override is required by the superclass AsyncReport.

        Provides the attributes (everything after the '?') part of the URI
        for the POST that initiates the report.
        """
        self.verify_attributes()
        attributes = (f'?start_date={self._start_date}&end_date={self._end_date}' +
                      '&metrics=' + ','.join(self._metrics))

        for attr, value in self.attrs.items():
            attributes += f'&{attr}={value}'

        return attributes
