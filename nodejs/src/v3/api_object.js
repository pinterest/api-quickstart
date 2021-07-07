import got from 'got'
import {ApiCommon} from '../api_common.js'
import {Input} from '../utils.js'

/**
 * The ApiObject uses the got library for REST transations:
 *   https://www.npmjs.com/package/got
 */
export class ApiObject extends ApiCommon {
  constructor(api_config, access_token) {
    super();
    this.api_uri = api_config.api_uri;
    this.api_config = api_config;
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
    const response = await this.get_response(path);
    return(response.data);
  }

  // Simple PUT transaction.
  async put_data(path, put_data) {
    const full_uri = this.api_uri + path;
    if (this.api_config.verbosity >= 2) {
      console.log('PUT', full_uri);
    }
    if (this.api_config.verbosity >= 3) {
      console.log(put_data);
    }
    try {
      const response = await got.put(full_uri, {
        headers: this.access_token.header(),
        json: put_data,
        followRedirect: false,
        responseType: 'json'
      });
      this.print_response(response);
      return response.body.data;
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }

  async delete_and_check(path) {
    if (this.api_config.verbosity >= 2) {
      console.log('DELETE', this.api_uri + path);
    }
    try {
      const response = await got.delete(this.api_uri + path, {
        headers: this.access_token.header(),
        followRedirect: false
      });
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }

  /**
   *  The iterator returned by this function implements paging on top of the bookmark
   *  functionality provided by the Pinterest API. Useful blog on async iterators:
   *    https://blog.risingstack.com/async-iterators-in-node-js/
   */
  get_iterator(path) {
    const api_object = this;
    return {
      [Symbol.asyncIterator]: async function*() {
        var path_with_query = null; // may not need to be initialized

        // first time: no bookmark
        var response = await api_object.get_response(path);

        // extend the path if there is a bookmark
        if (response.bookmark) {
          path_with_query = path + ((path.includes('?')) ? '&' : '?') + 'bookmark=';
        }

        while (true) {
          // send the current response to the function using the iterator
          for (const value of response.data) {
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
    }
  }

  /* Use the paged_iterator to print multiple objects. */
  async print_multiple(page_size, object_name, object_class, paged_iterator) {
    const input = new Input();
    var index = 1;
    var page_index = 1;
    try {
      for await (let object_data of paged_iterator) {
        // do this check after fetching a new page to make sure that there are more pins
        if (page_index > page_size) {
          if ('yes' == await input.one_of(`Continue printing ${object_name} list?`,
                                          ['yes', 'no'], 'yes')) {
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
