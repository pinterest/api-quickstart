import got from 'got'

export default class ApiObject {
  constructor(api_config, access_token) {
    this.api_uri = api_config.api_uri;
    this.access_token = access_token;
  }

  async request_data(path) {
    try {
      const response = await got.get(this.api_uri + path, {
        headers: this.access_token.header(),
        responseType: 'json'
      })
      console.log(`<Response [${response.statusCode}]>`);
      return response.body.data; // success
    } catch (error) {
      console.log(`<Response [${error.response.statusCode}]>`);
      console.log('request failed with reason:', error.response.body.message);
      return {};
    }
  }
}
