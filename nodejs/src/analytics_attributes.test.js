import { AnalyticsAttributes, AdAnalyticsAttributes } from './analytics_attributes.js';

describe('analytics_attributes tests', () => {
  test('analytics attributes', () => {
    const attributes = new AnalyticsAttributes();

    expect(() => {
      attributes.uri_attributes('ignored', false);
    }).toThrowError(new Error('start date not set'));

    expect(() => {
      attributes.data_attributes('ignored', false);
    }).toThrowError(new Error('start date not set'));

    attributes.start_date('oops');
    expect(() => {
      attributes.uri_attributes('ignored', false);
    }).toThrowError(
      new Error('start_date: oops needs to be a UTC date in YYYY-MM-DD format')
    );

    attributes.start_date('2021-93-24'); // matches YYYY-MM-DD but still not a date
    expect(() => {
      attributes.uri_attributes('ignored', false);
    }).toThrowError(
      new Error('start_date: 2021-93-24 needs to be a UTC date in YYYY-MM-DD format')
    );

    attributes.start_date('2021-05-01');
    expect(() => {
      attributes.uri_attributes('ignored', false);
    }).toThrowError('end date not set');

    attributes.end_date('2021-12-53');
    expect(() => {
      attributes.uri_attributes('ignored', false);
    }).toThrowError(
      new Error('end_date: 2021-12-53 needs to be a UTC date in YYYY-MM-DD format')
    );

    attributes.date_range('2021-05-31', '2021-05-01');
    expect(() => {
      attributes.uri_attributes('ignored', false);
    }).toThrowError(
      new Error('start date after end date')
    );

    jest.spyOn(global.Date, 'now')
      .mockImplementationOnce(() =>
        new Date('2021-05-31T09:22:43.762Z').valueOf()
      ); // for call to last_30_days

    attributes.last_30_days();
    expect(attributes.uri_attributes('ignored', false)).toEqual(
      'start_date=2021-05-01&end_date=2021-05-31'
    );

    expect(attributes.data_attributes('ignored', false)).toEqual({
      start_date: '2021-05-01',
      end_date: '2021-05-31'
    });

    expect(() => {
      attributes.uri_attributes('ignored', true);
    }).toThrowError(
      new Error('metrics not set')
    );

    attributes.metric('METRIC_2').metrics(new Set(['METRIC_3', 'METRIC_1']));
    expect(attributes.uri_attributes('statistics', true)).toEqual('\
start_date=2021-05-01&end_date=2021-05-31\
&statistics=METRIC_1,METRIC_2,METRIC_3');

    attributes.required_attrs.add('required_two');
    attributes.required_attrs.add('required_one');

    expect(() => {
      attributes.uri_attributes('ignored', true);
    }).toThrowError(
      new Error('missing attributes: required_one,required_two')
    );

    attributes.attrs.required_one = 'value_one';
    attributes.attrs.required_two = 'value_two';
    expect(attributes.uri_attributes('statistics', false)).toEqual('\
start_date=2021-05-01&end_date=2021-05-31\
&statistics=METRIC_1,METRIC_2,METRIC_3\
&required_one=value_one&required_two=value_two');

    attributes.enumerated_values.fibonacci = [1, 2, 3, 5, 8];
    attributes.attrs.fibonacci = 4;
    expect(() => {
      attributes.uri_attributes('ignored', true);
    }).toThrowError(
      new Error('fibonacci: 4 is not one of 1,2,3,5,8')
    );

    attributes.enumerated_values.animal = ['cat', 'dog', 'fish'];

    attributes.attrs.fibonacci = 5;
    attributes.attrs.animal = 'dog'; // of course, if you have to pick just one
    expect(attributes.uri_attributes('statistics', false)).toEqual('\
start_date=2021-05-01&end_date=2021-05-31\
&statistics=METRIC_1,METRIC_2,METRIC_3\
&animal=dog&fibonacci=5\
&required_one=value_one&required_two=value_two');

    expect(attributes.data_attributes('columns', false)).toEqual({
      start_date: '2021-05-01',
      end_date: '2021-05-31',
      columns: ['METRIC_1', 'METRIC_2', 'METRIC_3'],
      animal: 'dog',
      fibonacci: 5,
      required_one: 'value_one',
      required_two: 'value_two'
    });
  });

  test('ad analytics attributes', () => {
    const attributes = new AdAnalyticsAttributes()
      .date_range('2021-05-01', '2021-05-31')
      .granularity('MONTH')
      .click_window_days(1)
      .engagement_window_days(7)
      .view_window_days(14)
      .conversion_report_time('CONVERSION_EVENT');

    expect(attributes.uri_attributes('ignored', false)).toEqual('\
start_date=2021-05-01&end_date=2021-05-31\
&click_window_days=1\
&conversion_report_time=CONVERSION_EVENT\
&engagement_window_days=7\
&granularity=MONTH\
&view_window_days=14');

    attributes.click_window_days(42);
    expect(() => {
      attributes.uri_attributes('ignored', false);
    }).toThrowError(
      new Error('click_window_days: 42 is not one of 0,1,7,14,30,60')
    );
  });
});
