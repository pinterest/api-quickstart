import {ApiCommon} from './api_common';
import {RateLimitError} from './api_common';
import {RequestFailedError} from './api_common';
import {SpamError} from './api_common';

describe('api_common tests', () => {

  test('test print_response', () => {
    // check output
    console.log = jest.fn();

    const mock_api_config = jest.fn();
    mock_api_config.verbosity = 2;
    const api_common = new ApiCommon(mock_api_config);

    const mock_response = jest.fn();
    mock_response.statusCode = 418; // i'm a teapot!
    mock_response.headers = {'x-pinterest-rid': 'test-rid'};
    mock_response.body = 'test-response-body';
    api_common.print_response(mock_response);

    mock_api_config.verbosity = 3;
    api_common.print_response(mock_response);

    expect(console.log.mock.calls).toEqual([
      ['<Response [418]>'],
      ['<Response [418]>'],
      ['x-pinterest-rid:', 'test-rid'],
      ['test-response-body']
    ]);
  });

  test('test print_and_throw_error', () => {
    // check output
    console.log = jest.fn();

    const mock_api_config = jest.fn();
    mock_api_config.verbosity = 2;
    const api_common = new ApiCommon(mock_api_config);

    const mock_error = jest.fn();
    mock_error.response = {statusCode: 429, // spam error
                           headers: {
                             'x-pinterest-rid': 'test-429-rid'
                           },
                           body: {
                             message: 'hey there, slow down!',
                             message_detail: 'is u a Spammer?'
                           }
                          };
    try {
      api_common.print_and_throw_error(mock_error);
    } catch (error) {
      expect(error).toBeInstanceOf(SpamError);
      expect(error).toHaveProperty('message', 'is u a Spammer?');
    }

    expect(console.log.mock.calls).toEqual([
      ['<Response [429]>'],
      ['request failed with reason: hey there, slow down!'],
      ['x-pinterest-rid:', 'test-429-rid'],
      [mock_error.response.body]
    ]);

    mock_api_config.verbosity = 1;
    delete(mock_error.response.body.message_detail);
    console.log.mockReset();
    var error_message = 'request failed with reason: hey there, slow down!';

    try {
      api_common.print_and_throw_error(mock_error);
    } catch (error) {
      expect(error).toBeInstanceOf(RateLimitError);
      expect(error).toHaveProperty('message', error_message);
    }

    expect(console.log.mock.calls).toEqual([
      ['<Response [429]>'],
      [error_message]
    ]);

    console.log.mockReset()
    mock_error.response.statusCode = 401;
    mock_error.response.body.message = 'Trespassers W.';
    error_message = 'request failed with reason: Trespassers W.';

    try {
      api_common.print_and_throw_error(mock_error);
    } catch (error) {
      expect(error).toBeInstanceOf(RequestFailedError);
      expect(error).toHaveProperty('message', error_message);
    }

    expect(console.log.mock.calls).toEqual([
      ['<Response [401]>'],
      [error_message]
    ]);
  });
});
