import {ApiObject} from './api_object.js'

export class Board extends ApiObject {
  constructor(board_id, api_config, access_token) {
    super(api_config, access_token);
    this.board_id= board_id;
  }

  async get() {
    if (!this.board_id) {
      throw 'board_id must be set to get a board';
    }
    return this.request_data(`/v3/boards/${this.board_id}/`);
  }

  async get_pins() {
    return this.get_iterator(`/v3/boards/${this.board_id}/pins/`);
  }

  async get_sections() {
    return this.get_iterator(`/v3/board/${this.board_id}/sections/`);
  }

  async get_section_pins(section_id) {
    return this.get_iterator(`/v3/board/sections/${section_id}/pins/`);
  }

  static print_summary(board_data) {
    console.log('--- Board Summary ---');
    console.log('Board ID:', board_data.id);
    console.log('Name:', board_data.name);
    console.log('URL:', board_data.url);
    console.log('Category:', board_data.category);
    console.log('Description:', board_data.description);
    console.log('Pin Count:', board_data.pin_count);
    console.log('--------------------');
  }

  static print_section(section_data) {
    console.log('--- Board Section ---');
    console.log(`Section ID: ${section_data.id}`);
    console.log(`Title: ${section_data.title}`);
    console.log(`Pin Count: ${section_data.pin_count}`);
    console.log('---------------------');
  }

  static print_sections(sections_iterator) {
    for (const section of sections_iterator) {
      this.print_section(section);
    }
  }
}
