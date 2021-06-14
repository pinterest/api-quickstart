import got from 'got'
import {Input} from '../utils.js'

export class ApiObject {
  constructor(api_config, access_token) {
    this.api_uri = api_config.api_uri;
    this.api_config = api_config;
    this.access_token = access_token;
  }

  async get_response(path) {
    if (this.api_config.verbosity >= 2) {
      console.log('GET', path);
    }
    try {
      const response = await got.get(this.api_uri + path, {
        headers: this.access_token.header(),
        responseType: 'json'
      });
      if (this.api_config.verbosity >= 1) {
        console.log(`<Response [${response.statusCode}]>`);
        if (this.api_config.verbosity >= 3) {
          console.log(response.body);
        }
      }
      return response.body; // success
    } catch (error) {
      const error_message = 'request failed with reason: ' + error.response.body.message;
      if (this.api_config.verbosity >= 1) {
        console.log(`<Response [${error.response.statusCode}]>`);
        console.log(error_message);
        if (this.api_config.verbosity >= 2) {
          console.log(error.response.body);
        }
      }
      throw error_message;
    }
  }

  async request_data(path) {
    const response = await this.get_response(path);
    return(response.data);
  }

  /**
   *  This class implements paging on top of the bookmark functionality provided
   *  by the Pinterest API class. Useful blog on async iterators:
   *    https://blog.risingstack.com/async-iterators-in-node-js/
   */
  get_iterator(path) {
    const api_object = this;
    return {
      [Symbol.asyncIterator]: async function*() {
        var path_with_query = null; // may not need to be initialized

        // first time: no bookmark
        var response = await api_object.get_response(path);

        if (response.bookmark) {
          path_with_query = path + ((path.includes('?')) ? '&' : '?') + 'bookmark=';
        }

        while (true) {
          for (const value of response.data) {
            yield value;
          }
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
