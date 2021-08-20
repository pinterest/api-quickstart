import { Advertisers } from './advertisers.js';
import { ApiObject } from '../api_object.js';

jest.mock('../api_object');

describe('v5 advertisers tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v5 advertisers', async() => {
    const adv = new Advertisers('test_user', 'test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    // Need to use spyOn because Advertisers is a subclass of (extends) ApiObject.
    const mock_get_iterator = jest.spyOn(ApiObject.prototype, 'get_iterator');
    mock_get_iterator.mockResolvedValue('test_iterator');

    let response = await adv.get();
    expect(mock_get_iterator.mock.calls[0][0]).toEqual('/v5/ad_accounts');
    expect(response).toEqual('test_iterator');

    console.log = jest.fn(); // test output
    const elements = [
      { id: 'test_id_1', name: 'test_name_1' },
      { id: 'test_id_2', name: 'test_name_2', status: 'ACTIVE' }
    ];
    adv.print_summary(elements[0], 'thing 1');
    adv.print_summary(elements[1], 'thing 2');
    adv.print_enumeration(elements, 'frob');

    // verify output
    const summary1 = 'ID: test_id_1 | Name: test_name_1';
    const summary2 = 'ID: test_id_2 | Name: test_name_2 (ACTIVE)';
    expect(console.log.mock.calls).toEqual([
      [`thing 1 ${summary1}`],
      [`thing 2 ${summary2}`],
      [`[1] frob ${summary1}`],
      [`[2] frob ${summary2}`]
    ]);

    response = await adv.get_campaigns('ad_account_1');
    expect(mock_get_iterator.mock.calls[1][0]).toEqual(
      '/v5/ad_accounts/ad_account_1/campaigns');
    expect(response).toEqual('test_iterator');

    response = await adv.get_ad_groups('ad_account_2', 'campaign_2');
    expect(mock_get_iterator.mock.calls[2][0]).toEqual(
      '/v5/ad_accounts/ad_account_2/ad_groups?campaign_ids=campaign_2');
    expect(response).toEqual('test_iterator');

    response = await adv.get_ads('ad_account_3', 'campaign_3', 'ad_group_3');
    expect(mock_get_iterator.mock.calls[3][0]).toEqual('\
/v5/ad_accounts/ad_account_3/ads\
?campaign_ids=campaign_3&ad_group_ids=ad_group_3');
    expect(response).toEqual('test_iterator');
  });
});
