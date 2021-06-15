import got from 'got'
import {Input} from '../utils.js'

export class ApiObject {
  constructor(api_config, access_token) {
    this.api_uri = api_config.api_uri;
    this.api_config = api_config;
    this.access_token = access_token;
  }

  print_response(response) {
    if (this.api_config.verbosity >= 1) {
      console.log(`<Response [${response.statusCode}]>`);
      if (this.api_config.verbosity >= 3) {
        console.log(response.body);
      }
    }
  }

  print_and_throw_error(error) {
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

  async request_data(path) {
    const response = await this.get_response(path);
    return(response.data);
  }

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
