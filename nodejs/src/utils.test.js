import {Input} from './utils';
import readline from 'readline';

jest.mock('readline');

describe('Input tests', () => {

  test('test input methods', async () => {
    // check output
    console.log = jest.fn();

    const mock_rl_interface = jest.fn();
    readline.createInterface.mockReturnValue(mock_rl_interface);

    mock_rl_interface.question = jest.fn();
    mock_rl_interface.close = jest.fn();
    mock_rl_interface.question
      .mockImplementationOnce((_query, cb) => cb('CaT'))
      .mockImplementationOnce((_query, cb) => cb('fish'))
      .mockImplementationOnce((_query, cb) => cb(''))
      .mockImplementationOnce((_query, cb) => cb('hello, world'));

    const test_list = ['DOG', 'CAT', 'BIRD'];

    const input = new Input();

    expect('CAT').toEqual(await input.one_of('animal?', test_list, 'BIRD'));
    expect('BIRD').toEqual(await input.one_of('test 2', test_list, 'BIRD'));
    expect('hello, world').toEqual(await input.get('printf says?'));

    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[0][0]);
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[1][0]);
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[2][0]);
    expect('printf says?').toEqual(mock_rl_interface.question.mock.calls[3][0]);

    expect(console.log.mock.calls).toEqual([
      ['animal?'],
      ['test 2'],
      ['input must be one of', test_list]
    ]);

    input.close();
    expect(mock_rl_interface.close.mock.calls.length === 1);
  });
});
