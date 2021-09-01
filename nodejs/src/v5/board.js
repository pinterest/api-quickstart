import { ApiObject } from '../api_object.js';

export class Board extends ApiObject {
  constructor(board_id, api_config, access_token) {
    super(api_config, access_token);
    this.board_id = board_id;
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/boards/get
  async get() {
    if (!this.board_id) {
      throw new Error('board_id must be set to get a board');
    }
    return this.request_data(`/v5/boards/${this.board_id}`);
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/boards/list_pins
  async get_pins() {
    return this.get_iterator(`/v5/boards/${this.board_id}/pins`);
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list
  async get_sections() {
    return this.get_iterator(`/v5/boards/${this.board_id}/sections`);
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list_pins
  async get_section_pins(section_id) {
    return this.get_iterator(`/v5/boards/${this.board_id}/sections/${section_id}/pins`);
  }

  static print_summary(board_data) {
    console.log('--- Board Summary ---');
    console.log('Board ID:', board_data.id);
    console.log('Name:', board_data.name);
    console.log('Description:', board_data.description);
    console.log('Owner:', board_data.owner.username);
    console.log('Privacy:', board_data.privacy);
    console.log('--------------------');
  }

  // provides a human-readable identifier for a board
  static text_id(board_data) {
    // simulate v3 URL to provide a text identifier
    return `/${board_data.owner.username}/` +
            board_data.name.toLowerCase().replaceAll(' ', '-') + '/';
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/boards/create
  async create(board_data) {
    const OPTIONAL_ATTRIBUTES = [
      'description',
      'privacy'
    ];
    const create_data = {
      name: board_data.name
    };
    for (const key of OPTIONAL_ATTRIBUTES) {
      const value = board_data[key];
      if (value) {
        create_data[key] = value;
      }
    }

    const new_board_data = await this.post_data('/v5/boards', create_data);
    this.board_id = new_board_data.id;
    return new_board_data;
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/boards/delete
  async delete() {
    await this.delete_and_check(`/v5/boards/${this.board_id}`);
  }

  static print_section(section_data) {
    console.log('--- Board Section ---');
    console.log('Section ID:', section_data.id);
    console.log('Name:', section_data.name);
    console.log('---------------------');
  }

  static print_sections(sections_iterator) {
    for (const section of sections_iterator) {
      this.print_section(section);
    }
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/board_sections/create
  async create_section(section_data) {
    const create_data = {
      name: section_data.name
    };
    return this.post_data(`/v5/boards/${this.board_id}/sections`, create_data);
  }
}
