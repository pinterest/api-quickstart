import got from 'got';
import { ApiCommon } from './api_common.js';
import { Input } from './utils.js';

/**
 * The ApiObject uses the got library for REST transations:
 *   https://www.npmjs.com/package/got
 */
export class ApiObject extends ApiCommon {
  constructor(api_config, access_token) {
    super(api_config);
    this.api_uri = api_config.api_uri;
    this.access_token = access_token;
  }

  // Code that is common to a simple GET as in response_data()
  // or to a bookmarked GET as in get_iterator().
  async get_response(path) {
    const full_uri = this.api_uri + path;
    if (this.api_config.verbosity >= 2) {
      console.log('GET', full_uri);
    }
    try {
      const response = await got.get(full_uri, {
        headers: this.access_token.header(),
        followRedirect: false,
        responseType: 'json'
      });
      this.print_response(response);
      return response.body; // success
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }

  // Simple GET transaction.
  async request_data(path) {
    return await this.get_response(path);
  }

  // Simple PUT transaction.
  async put_data(path, put_data) {
    const full_uri = this.api_uri + path;
    if (this.api_config.verbosity >= 2) {
      console.log('PUT', full_uri);
      if (this.api_config.verbosity >= 3) {
        console.log(JSON.stringify(put_data));
      }
    }
    try {
      const response = await got.put(full_uri, {
        headers: this.access_token.header(),
        json: put_data,
        followRedirect: false,
        responseType: 'json'
      });
      this.print_response(response);
      return response.body;
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }

  // Simple POST transaction.
  async post_data(path, post_data) {
    const full_uri = this.api_uri + path;
    if (this.api_config.verbosity >= 2) {
      console.log('POST', full_uri);
      if (this.api_config.verbosity >= 3) {
        console.log(JSON.stringify(post_data));
      }
    }
    try {
      const response = await got.post(full_uri, {
        headers: this.access_token.header(),
        json: post_data,
        followRedirect: false,
        responseType: 'json'
      });
      this.print_response(response);
      return response.body;
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }

  async delete_and_check(path) {
    if (this.api_config.verbosity >= 2) {
      console.log('DELETE', this.api_uri + path);
    }
    try {
      await got.delete(this.api_uri + path, {
        headers: this.access_token.header(),
        followRedirect: false
      });
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }

  // Reset the exponential backoff algorithm.
  reset_backoff() {
    this.backoff = 1; // delay for backoff algorithm in seconds
    this.backoff_string = 'a second'; // for human-readable output of delay
  }

  // Provides an exponential backoff algorithm (up to a 10 second maximum delay)
  // to determine the appropriate amount of time to wait between asynchronous
  // API requests.
  async wait_backoff({ message }) {
    if (message) {
      console.log(`${message} Waiting ${this.backoff_string}...`);
    }

    await new Promise(resolve => setTimeout(resolve, this.backoff * 1000));
    this.backoff = Math.min(this.backoff * 2, 10);
    this.backoff_string = `${this.backoff} seconds`;
  }

  // Concatenate the query parameters to the path with appropriate delimiters.
  add_query(path, query_parameters) {
    if (query_parameters) {
      // for backward compatibility, surface query_parameters from inside object
      if (query_parameters.query_parameters) {
        query_parameters = query_parameters.query_parameters;
      }
      const query = new URLSearchParams(query_parameters).toString();
      if (query) {
        const delimiter = path.includes('?') ? '&' : '?';
        path += delimiter + query;
      }
    }
    return path;
  }

  /**
   *  The iterator returned by this function implements paging on top of the bookmark
   *  functionality provided by the Pinterest API. Useful blog on async iterators:
   *    https://blog.risingstack.com/async-iterators-in-node-js/
   */
  get_iterator(path, query_parameters) {
    path = this.add_query(path, query_parameters);
    const api_object = this;
    return {
      [Symbol.asyncIterator]: async function * () {
        let path_with_query = null; // may not need to be initialized

        // first time: no bookmark
        let response = await api_object.get_response(path);

        // extend the path if there is a bookmark
        if (response.bookmark) {
          path_with_query = path + (path.includes('?') ? '&' : '?') + 'bookmark=';
        }

        while (true) {
          // send the current response to the function using the iterator
          for (const value of response.items) {
            yield value;
          }
          // continue the loop if the current response has a bookmark, otherwise done
          if (response.bookmark) {
            response = await api_object.get_response(path_with_query + response.bookmark);
          } else {
            break;
          }
        }
      }
    };
  }

  /* Use the paged_iterator to print multiple objects. */
  async print_multiple(page_size, object_name, object_class, paged_iterator) {
    const input = new Input();
    let index = 1;
    let page_index = 1;
    try {
      for await (const object_data of paged_iterator) {
        // do this check after fetching a new page to make sure that there are more pins
        if (page_index > page_size) {
          if (await input.one_of(`Continue printing ${object_name} list?`,
            ['yes', 'no'], 'yes') === 'yes') {
            page_index = 1;
          } else {
            break;
          }
        }
        // print the object
        process.stdout.write(`[${index}] `);
        object_class.print_summary(object_data);

        // increment counters
        index++;
        page_index++;
      }
    } finally {
      input.close();
    }
  }
}
