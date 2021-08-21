import { Input } from './utils';
import fs from 'fs';
import readline from 'readline';

jest.mock('fs');
jest.mock('readline');

describe('Input tests', () => {
  test('one_of and get methods', async() => {
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
      .mockImplementationOnce((_query, cb) => cb('hello, world'));

    /* eslint-enable node/no-callback-literal */

    const test_list = ['DOG', 'CAT', 'BIRD'];

    const input = new Input();

    // test input.one_of
    expect('CAT').toEqual(await input.one_of('animal?', test_list, 'BIRD'));
    expect('BIRD').toEqual(await input.one_of('test 2', test_list, 'BIRD'));

    // test input.get
    expect('hello, world').toEqual(await input.get('printf says?'));

    // check the prompts sent via the question function
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[0][0]);
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[1][0]);
    expect('[BIRD] ').toEqual(mock_rl_interface.question.mock.calls[2][0]);
    expect('printf says?').toEqual(mock_rl_interface.question.mock.calls[3][0]);

    // check the prompts and error messages sent via the console
    expect(console.log.mock.calls).toEqual([
      ['animal?'],
      ['test 2'],
      ['input must be one of', test_list]
    ]);

    input.close();
    expect(mock_rl_interface.close.mock.calls.length).toBe(1);
  });

  test('number method', async() => {
    // check output
    console.log = jest.fn();

    const mock_rl_interface = jest.fn();
    readline.createInterface.mockReturnValue(mock_rl_interface);

    mock_rl_interface.question = jest.fn();
    mock_rl_interface.close = jest.fn();
    /* eslint-disable node/no-callback-literal -- eslint incorrectly detects cb as error callback */
    mock_rl_interface.question
      .mockImplementationOnce((_query, cb) => cb('2'))
      .mockImplementationOnce((_query, cb) => cb(''))
      .mockImplementationOnce((_query, cb) => cb('oops'))
      .mockImplementationOnce((_query, cb) => cb('-4'))
      .mockImplementationOnce((_query, cb) => cb('42'))
      .mockImplementationOnce((_query, cb) => cb('5'));

    /* eslint-enable node/no-callback-literal */

    const input = new Input();

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
    expect('[3] ').toEqual(mock_rl_interface.question.mock.calls[0][0]);
    expect('[3] ').toEqual(mock_rl_interface.question.mock.calls[1][0]);
    expect('[3] ').toEqual(mock_rl_interface.question.mock.calls[2][0]);

    // check the prompts and error messages sent via the console
    expect(console.log.mock.calls).toEqual([
      ['should return 2'],
      ['should return 3'],
      ['should return -4'],
      ['oops is not a number between -5 and 23'],
      ['check out of range'],
      ['42 is not a number between -5 and 23']
    ]);

    input.close();
  });

  // This test executes three mocked calls to input.number to test all
  // of the different conditionals. Search down for "test input.number"
  // for documentation on each of the three scenarios.
  test('path_for_write method', async() => {
    // check output
    console.log = jest.fn();

    const mock_rl_interface = jest.fn();
    readline.createInterface.mockReturnValue(mock_rl_interface);

    mock_rl_interface.question = jest.fn();
    mock_rl_interface.close = jest.fn();
    /* eslint-disable node/no-callback-literal -- eslint incorrectly detects cb as error callback */
    mock_rl_interface.question
      // first call to path_for_write
      .mockImplementationOnce((_query, cb) => cb('testfile1'))

      // second call to path_for_write
      .mockImplementationOnce((_query, cb) => cb('testfile2'))
      .mockImplementationOnce((_query, cb) => cb('no'))
      .mockImplementationOnce((_query, cb) => cb(''))
      .mockImplementationOnce((_query, cb) => cb('yes'))
      .mockImplementationOnce((_query, cb) => cb('testfile3'))
      .mockImplementationOnce((_query, cb) => cb('yes'))

      // third call to path_for_write
      .mockImplementationOnce((_query, cb) => cb('testfile4'))
      .mockImplementationOnce((_query, cb) => cb('testfile5'));

    fs.open
      // first call to path_for_write
      .mockImplementationOnce(
        (path, mode, cb) => cb(null, 'testfd1'))

      // second call to path_for_write
      .mockImplementationOnce(
        (path, mode, cb) => cb({ code: 'EEXIST' }, null))
      .mockImplementationOnce(
        (path, mode, cb) => cb({ code: 'EEXIST' }, null))
      .mockImplementationOnce(
        (path, mode, cb) => cb({ code: 'OTHER_ERROR' }, null))
      .mockImplementationOnce(
        (path, mode, cb) => cb({ code: 'EEXIST' }, null))
      .mockImplementationOnce(
        (path, mode, cb) => cb(null, 'testfd2'))

      // third call to path_for_write
      .mockImplementationOnce(
        (path, mode, cb) => cb({ code: 'OTHER_ERROR' }, null))
      .mockImplementationOnce(
        (path, mode, cb) => cb(null, 'testfd3'));

    /* eslint-enable node/no-callback-literal */

    const input = new Input();

    // test input.number
    // first call: success on the first time
    expect('testfile1').toEqual(
      await input.path_for_write('should return testfile1', 'default1'));

    // second call:
    // * first file (testfile2) exists and mock user says not to overwrite
    // * second file (default2) exists, mock user says to overwrite,
    //   but then there is some sort of error opening the file for write
    // * third file (testfile3) exists, mock user says to overwrite,
    //   and the open is successful
    expect('testfile3').toEqual(
      await input.path_for_write('should return testfile3', 'default2'));

    // third call:
    // * first file (testfile4) open is not successful
    // * second file (testfile5) open is successful
    expect('testfile5').toEqual(
      await input.path_for_write('should return testfile5', 'default3'));

    // check the prompts sent via the question function
    // first call to path_for_write
    expect('[default1] ')
      .toEqual(mock_rl_interface.question.mock.calls[0][0]);

    // second call to path_for_write
    expect('[default2] ')
      .toEqual(mock_rl_interface.question.mock.calls[1][0]);
    expect('[no] ')
      .toEqual(mock_rl_interface.question.mock.calls[2][0]);
    expect('[default2] ')
      .toEqual(mock_rl_interface.question.mock.calls[3][0]);
    expect('[no] ')
      .toEqual(mock_rl_interface.question.mock.calls[4][0]);
    expect('[default2] ')
      .toEqual(mock_rl_interface.question.mock.calls[5][0]);
    expect('[no] ')
      .toEqual(mock_rl_interface.question.mock.calls[6][0]);

    // third call to path_for_write
    expect('[default3] ')
      .toEqual(mock_rl_interface.question.mock.calls[7][0]);
    expect('[default3] ')
      .toEqual(mock_rl_interface.question.mock.calls[8][0]);

    // check open calls
    // first call to path_for_write
    expect(fs.open.mock.calls[0][0]).toEqual('testfile1');
    expect(fs.open.mock.calls[0][1]).toEqual('wx');

    // second call to path_for_write
    expect(fs.open.mock.calls[1][0]).toEqual('testfile2');
    expect(fs.open.mock.calls[1][1]).toEqual('wx');
    expect(fs.open.mock.calls[2][0]).toEqual('default2');
    expect(fs.open.mock.calls[2][1]).toEqual('wx');
    expect(fs.open.mock.calls[3][0]).toEqual('default2');
    expect(fs.open.mock.calls[3][1]).toEqual('w');
    expect(fs.open.mock.calls[4][0]).toEqual('testfile3');
    expect(fs.open.mock.calls[4][1]).toEqual('wx');
    expect(fs.open.mock.calls[5][0]).toEqual('testfile3');
    expect(fs.open.mock.calls[5][1]).toEqual('w');

    // third call to path_for_write
    expect(fs.open.mock.calls[6][0]).toEqual('testfile4');
    expect(fs.open.mock.calls[6][1]).toEqual('wx');
    expect(fs.open.mock.calls[7][0]).toEqual('testfile5');
    expect(fs.open.mock.calls[7][1]).toEqual('wx');

    // check to make sure that the file is closed properly
    expect(fs.close.mock.calls).toEqual([
      ['testfd1'],
      ['testfd2'],
      ['testfd3']
    ]);

    // check the prompts and error messages sent via the console
    expect(console.log.mock.calls).toEqual([
      // first call to path_for_write
      ['should return testfile1'],

      // second call to path_for_write
      ['should return testfile3'],
      ['Overwrite this file?'],
      ['Overwrite this file?'],
      ['Error: can not write to this file.'],
      ['Overwrite this file?'],

      // third call to path_for_write
      ['should return testfile5'],
      ['Error: can not write to this file.']
    ]);

    input.close();
  });
});
