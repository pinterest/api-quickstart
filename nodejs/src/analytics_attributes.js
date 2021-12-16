/**
 * The two classes in this module (AnalyticsAttributes and AdAnalyticsAttributes)
 * provide common parameters for API v3, v4, and v5 synchronous and asynchronous
 * reports. AnalyticsAttributes implements parameters that are common to all
 * reports; AdAnalyticsAttributes extents AnalyticsAttributes to implement
 * parameters for all advertising reports.
 *
 * Class Diagram (the arrow indicates a parent->child relationship)
 *    AnalyticsAttributes
 *    -> Analytics(v3)
 *    -> Analytics(v5)
 *    -> AdAnalyticsAttributes
 *       -> AdAnalytics(v3/v4)
 *       -> AdAnalytics(v5)
 *       -> DeliveryMetricsAsyncReport(v3 only)
 *
 */

// This class profiles common variables and functions related
// to the metrics returned by analytics endpoints.
export class AnalyticsAttributes {
  constructor() {
    this._start_date = null;
    this._end_date = null;
    this.enumerated_values = {};
    this.required_attrs = new Set();
    this.attrs = {};
    this._metrics = new Set();
  }

  // Check that the value of an enumerated attribute is an expected value.
  check_enumerated_attr(name, value) {
    const values = this.enumerated_values[name];
    if (!values) {
      return; // nothing to check
    }
    if (!values.includes(value)) {
      throw new Error(`${name}: ${value} is not one of ${values}`);
    }
  }

  // Check the values of all of the enumerated attributes that have been
  // set with their expected values.
  check_enumerated_attrs() {
    for (const [attr, value] of Object.entries(this.attrs)) {
      this.check_enumerated_attr(attr, value);
    }
  }

  // Verify that the required attributes are set.
  check_required_attrs() {
    const missing = new Set();
    this.required_attrs.forEach(required_attr => {
      if (!this.attrs[required_attr]) {
        missing.add(required_attr);
      }
    });
    if (missing.size !== 0) {
      const missing_array = Array.from(missing);
      missing_array.sort(); // sort makes error testing and debugging easier
      throw new Error(`missing attributes: ${missing_array}`);
    }
  }

  // Required attribute. Report start date (UTC): YYYY-MM-DD.
  start_date(start_date) {
    this._start_date = start_date;
    return this;
  }

  // Required attribute. Report end date (UTC): YYYY-MM-DD.
  end_date(end_date) {
    this._end_date = end_date;
    return this;
  }

  // Shortcut: set required start date and end date in one call.
  date_range(start_date, end_date) {
    this._start_date = start_date;
    this._end_date = end_date;
    return this;
  }

  // Shortcut: set the end date to the current date and the start date
  // to thirty days earlier.
  last_30_days() {
    const now_msec = Date.now(); // easily mocked in unit tests
    const now = new Date(now_msec);
    const now_minus_30 = new Date(now_msec);
    now_minus_30.setDate(now_minus_30.getDate() - 30);
    this.date_range(
      now_minus_30.toISOString().slice(0, 10),
      now.toISOString().slice(0, 10)
    );
    return this;
  }

  // Verify that a date attribute is correctly formatted
  // as a YYYY-MM-DD date.
  check_date_attr(name, date_string) {
    const date_format = /^\d{4}-\d{2}-\d{2}$/; // YYYY-MM-DD

    // Checking the format is important, because Date will parse
    // lots of formats that will not work with the Pinterest API.
    if (date_string.search(date_format) === 0) {
      // date_string could be a date, but does it parse?
      const date = new Date(date_string);
      if (date.getTime() > 0) {
        // date_string parses as a date. However...
        // Date parsing is implementation specific, so converting back to
        // a string might correct the date. For example, 2021-02-31 might
        // become 2021-03-03.
        return date.toISOString().slice(0, 10);
      }
    }

    // at least one check failed
    throw new Error(
      `${name}: ${date_string} needs to be a UTC date in YYYY-MM-DD format`
    );
  }

  // Not always required, but strongly advised. May be set to 'ALL'.
  metrics(metrics) {
    this._metrics = new Set([...this._metrics, ...metrics]); // union
    return this;
  }

  // Adds a single metric to the metric set.
  metric(metric) {
    this._metrics.add(metric);
    return this;
  }

  // Returns the metrics as a comma-separated string, suitable
  // for a GET or POST parameter.
  metrics_string(required) {
    if (this._metrics.size === 0) {
      // throw an exception if metrics are required but not set
      if (required) {
        throw new Error('metrics not set');
      }
      return null;
    }

    // set order is nondeterministic, so create a sorted array
    const metrics_array = Array.from(this._metrics);
    metrics_array.sort(); // sort makes error testing and debugging easier
    return metrics_array.join(',');
  }

  // check all of the attributes
  verify_attributes(metrics_required) {
    // check the required start and end date attributes
    if (!this._start_date) {
      throw new Error('start date not set');
    }
    this._start_date = this.check_date_attr('start_date', this._start_date);

    if (!this._end_date) {
      throw new Error('end date not set');
    }
    this._end_date = this.check_date_attr('end_date', this._end_date);
    if (this._start_date > this._end_date) {
      throw new Error('start date after end date');
    }

    // check to make sure all of the required attributes are set
    this.check_required_attrs();

    // check all of the attributes with enumerated values
    this.check_enumerated_attrs();
  }

  // Provides the attributes (everything after the '?') part of the URI
  // for the GET or POST that requests or initiates the report.
  //
  // Note: This function does not include the leading '?' so that it
  // can combined with a prefixed query if necessary.
  uri_attributes(metrics_parameter, metrics_required) {
    this.verify_attributes(metrics_required);

    let attributes = `start_date=${this._start_date}&end_date=${this._end_date}`;

    const metrics = this.metrics_string(metrics_required);
    if (metrics) {
      attributes += `&${metrics_parameter}=${metrics}`;
    }

    // sort attributes to make order deterministic for testing
    const attr_array = Array.from(Object.keys(this.attrs));
    attr_array.sort(); // sort makes error testing and debugging easier
    for (const attr of attr_array) {
      attributes += `&${attr}=${this.attrs[attr]}`;
    }

    return attributes;
  }
}

// This class extends the basic metrics to include standard
// advertising metrics.
export class AdAnalyticsAttributes extends AnalyticsAttributes {
  constructor() {
    super();

    const ENUMERATED_WINDOW_DAYS = [0, 1, 7, 14, 30, 60];

    // This dictionary lists values for attributes that are enumerated
    // in the API documentation. The keys are the names of the attributes,
    // and the dictionary values are sets of API-defined values.
    Object.assign(this.enumerated_values, {
      granularity: ['TOTAL', 'DAY', 'HOUR', 'WEEK', 'MONTH'],
      click_window_days: ENUMERATED_WINDOW_DAYS,
      engagement_window_days: ENUMERATED_WINDOW_DAYS,
      view_window_days: ENUMERATED_WINDOW_DAYS
    });
  }

  granularity(granularity) {
    // TOTAL - metrics are aggregated over the specified date range.
    // DAY - metrics are broken down daily.
    // HOUR - metrics are broken down hourly.
    // WEEK - metrics are broken down weekly.
    // MONTH - metrics are broken down monthly.
    // Currently, we only support hourly breakdown when data_source=REALTIME.

    this.attrs.granularity = granularity;
    return this;
  }

  click_window_days(click_window_days) {
    // Number of days to use as the conversion attribution window for a 'click' action.
    // Applies to Pinterest Tag conversion metrics. Prior conversion tags use their
    // defined attribution windows. If not specified, defaults to 30 days.

    this.attrs.click_window_days = click_window_days;
    return this;
  }

  engagement_window_days(engagement_window_days) {
    // Number of days to use as the conversion attribution window for an engagement
    // action. Engagements include saves, pin clicks, and carousel card swipes.
    // Applies to Pinterest Tag conversion metrics. Prior conversion tags use
    // their defined attribution windows. If not specified, defaults to 30 days.

    this.attrs.engagement_window_days = engagement_window_days;
    return this;
  }

  view_window_days(view_window_days) {
    // Number of days to use as the conversion attribution window for
    // a view action. Applies to Pinterest Tag conversion metrics. Prior
    // conversion tags use their defined attribution windows. If not specified,
    // defaults to 1 day.

    this.attrs.view_window_days = view_window_days;
    return this;
  }

  conversion_report_time(conversion_report_time) {
    // The date by which the conversion metrics returned from this endpoint
    // will be reported. There are two dates associated with a conversion event:
    // the date that the user interacted with the ad, and the date that the user
    // completed a conversion event.

    this.attrs.conversion_report_time = conversion_report_time;
    return this;
  }
}
