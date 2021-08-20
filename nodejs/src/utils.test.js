import { Input } from './utils';
import readline from 'readline';

jest.mock('readline');

describe('Input tests', () => {
  test('input methods', async() => {
    // check output
    console.log = jest.fn();

    const mock_rl_interface = jest.fn();
    readline.createInterface.mockReturnValue(mock_rl_interface);

    mock_rl_interface.question = jest.fn();
    mock_rl_interface.close = jest.fn();
    /* eslint-disable node/no-callback-literal -- eslint incorrectly detects cb as error callback */
    mock_rl_interface.question
      .mockImplementationOnce((_query, cb) => cb('CaT'))

      .mockImplementationOnce((_query, cb) => cb('fish'))
      .mockImplementationOnce((_query, cb) => cb(''))
      .mockImplementationOnce((_query, cb) => cb('hello, world'))
      .mockImplementationOnce((_query, cb) => cb('2'))
      .mockImplementationOnce((_query, cb) => cb(''))
      .mockImplementationOnce((_query, cb) => cb('oops'))
      .mockImplementationOnce((_query, cb) => cb('-4'))
      .mockImplementationOnce((_query, cb) => cb('42'))
      .mockImplementationOnce((_query, cb) => cb('5'));

    /* eslint-enable node/no-callback-literal */

    const test_list = ['DOG', 'CAT', 'BIRD'];

    const input = new Input();

    // test input.one_of
    expect('CAT').toEqual(await input.one_of('animal?', test_list, 'BIRD'));
    expect('BIRD').toEqual(await input.one_of('test 2', test_list, 'BIRD'));

    // test input.get
    expect('hello, world').toEqual(await input.get('printf says?'));

    // test input.number
    expect(2).toEqual(await input.number('should return 2', -5, 23, 3));
    expect(3).toEqual(await input.number('should return 3', -5, 23, 3));
    expect(-4).toEqual(await input.number('should return -4', -5, 23, 3));
    expect(5).toEqual(await input.number('check out of range', -5, 23, 3));
    expect(6).toEqual(await input.number('degenerate range', 6, 6, 100));
    await expect(async() => {
      await input.number('should throw error', 23, 8);
    }).rejects.toThrowError(new Error('minimum 23 > maximum 8'));

    // check the prompts sent via the question function
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[0][0]);
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[1][0]);
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[2][0]);
    expect('printf says?').toEqual(mock_rl_interface.question.mock.calls[3][0]);
    expect('[3] ').toEqual(mock_rl_interface.question.mock.calls[4][0]);
    expect('[3] ').toEqual(mock_rl_interface.question.mock.calls[5][0]);
    expect('[3] ').toEqual(mock_rl_interface.question.mock.calls[6][0]);

    // check the prompts and error messages sent via the console
    expect(console.log.mock.calls).toEqual([
      ['animal?'],
      ['test 2'],
      ['input must be one of', test_list],
      ['should return 2'],
      ['should return 3'],
      ['should return -4'],
      ['oops is not a number between -5 and 23'],
      ['check out of range'],
      ['42 is not a number between -5 and 23']
    ]);

    input.close();
    expect(mock_rl_interface.close.mock.calls.length).toBe(1);
  });
});
