import { ApiObject } from './api_object.js';

export class Terms extends ApiObject {
  // https://developers.pinterest.com/docs/api/v5/#tag/terms

  async get_related(terms) {
    const path = super.add_query('/v5/terms/related', { terms: terms });
    return await super.request_data(path);
  }

  print_related_terms(related_terms) {
    console.log('--- Related Terms ---');
    console.log('First Input Term:', related_terms.id);
    console.log('Count:', related_terms.related_term_count);
    for (const entry of related_terms.related_terms_list) {
      console.log('Term:', entry.term);
      for (const related_term of entry.related_terms) {
        console.log('  Related Term:', related_term);
      }
    }
    console.log('----------------------');
  }

  async get_suggested(terms, { limit }) {
    const query = { term: terms };
    if (limit) {
      query.limit = limit;
    }
    const path = super.add_query('/v5/terms/suggested', query);
    return await super.request_data(path);
  }

  print_suggested_terms(suggested_terms) {
    console.log('--- Suggested Terms ---');
    for (const term of suggested_terms) {
      console.log('Term:', term);
    }
    console.log('-----------------------');
  }
}
