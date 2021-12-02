export class SpamError extends Error {
  constructor(message) {
    super(message);
    this.name = 'SpamError';
  }
}

export class RateLimitError extends Error {
  constructor(message) {
    super(message);
    this.name = 'RateLimitError';
  }
}

export class RequestFailedError extends Error {
  constructor(message) {
    super(message);
    this.name = 'RequestFailedError';
  }
}

export class ApiCommon {
  constructor(api_config) {
    this.api_config = api_config;
  }

  // common code for printing the response to a successful transaction
  print_response(response) {
    if (this.api_config.verbosity >= 1) {
      console.log(`<Response [${response.statusCode}]>`);
      if (this.api_config.verbosity >= 3) {
        console.log('x-pinterest-rid:', response.headers['x-pinterest-rid']);
        console.log(response.body);
      }
    }
  }

  // common code for printing and rethrowing the error in response to a transaction
  print_and_throw_error(error) {
    if (!error) {
      throw new RequestFailedError('unknown error');
    }
    if (!error.response) {
      console.log('error:', error);
      throw new RequestFailedError('error without a response');
    }
    if (!error.response.body) {
      console.log('error response:', error.response);
      throw new RequestFailedError('error without a response body');
    }
    if (!error.response.body.message) {
      console.log('error response body:', error.response.body);
      throw new RequestFailedError('error without a response body message');
    }
    const error_message = `request failed with reason: ${error.response.body.message}`;
    if (this.api_config.verbosity >= 1) {
      console.log(`<Response [${error.response.statusCode}]>`);
      console.log(error_message);
      if (this.api_config.verbosity >= 2) {
        console.log('x-pinterest-rid:', error.response.headers['x-pinterest-rid']);
        console.log(error.response.body);
      }
    }
    if (error.response.statusCode === 429) {
      const detail = error.response.body.message_detail || error.response.body.message;
      if (detail && detail.toLowerCase().includes('spam')) {
        throw new SpamError(detail);
      }
      throw new RateLimitError(error_message);
    }
    throw new RequestFailedError(error_message);
  }
}
