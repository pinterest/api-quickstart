import unittest
import mock
from mock import call
from src.utils import input_number, input_one_of, input_path_for_write

class GenericRequestsTest(unittest.TestCase):

    @mock.patch('builtins.print')
    @mock.patch('builtins.input')
    def test_input_number(self, mock_input, mock_print):
        mock_input.side_effect = ['2', '', 'oops', '-4', '42', '5']

        self.assertEqual(2, input_number('should return 2', -5, 23, 3))
        mock_input.assert_called_once_with('[3] ')
        mock_print.assert_called_once_with('should return 2')
        mock_print.reset_mock()

        self.assertEqual(3, input_number('should return 3', -5, 23, 3))
        mock_print.assert_called_once_with('should return 3')
        mock_print.reset_mock()

        self.assertEqual(-4, input_number('should return -4', -5, 23, 3))
        mock_print.assert_any_call('oops is not an integer')
        mock_print.reset_mock()

        self.assertEqual(5, input_number('check out of range', -5, 23))
        mock_print.assert_any_call('42 is not between -5 and 23')
        mock_print.reset_mock()

        self.assertEqual(6, input_number('degenerate range', 6, 6))

        with self.assertRaisesRegex(ValueError, 'minimum 23 > maximum 8'):
            input_number('should throw exception', 23, 8)

    @mock.patch('builtins.print')
    @mock.patch('builtins.input')
    def test_input_one_of(self, mock_input, mock_print):
        mock_input.side_effect = ['CaT', 'fish', '']

        test_list = ['DOG', 'CAT', 'BIRD']

        self.assertEqual('CAT', input_one_of('animal?', test_list, 'BIRD'))
        mock_input.assert_called_once_with('[BIRD] ')
        mock_print.assert_called_once_with('animal?')
        mock_print.mock_reset()

        self.assertEqual('BIRD', input_one_of('test 2', test_list, 'BIRD'))
        mock_print.assert_any_call(f'input must be one of {test_list}')
        mock_print.mock_reset()

    @mock.patch('os.path.exists')
    @mock.patch('builtins.open')
    @mock.patch('builtins.print')
    @mock.patch('builtins.input')
    def test_input_path_for_write(self, mock_input, mock_print, mock_open, mock_exists):
        mock_input.side_effect = ['/path/to/file1', # test case 1
                                  '/path/to/file2', 'yes', # test case 2
                                  '/path/to/file3', '/path/to/file4', # test case 3
                                  '', 'no', '', 'yes' # test case 4
                                  ] 
        mock_exists.side_effect = [False,
                                   True,
                                   False, False,
                                   True, True]
        
        mock_file = mock.MagicMock()
        mock_open.side_effect = [mock_file,
                                 mock_file,
                                 OSError('open failed. sorry!'), mock_file,
                                 mock_file]

        # test case 1
        self.assertEqual('/path/to/file1', input_path_for_write('test file 1', '/default/file'))
        mock_open.assert_called_once_with('/path/to/file1', 'w')
        mock_print.assert_called_once_with('test file 1')
        mock_print.mock_reset()

        # test case 2
        self.assertEqual('/path/to/file2', input_path_for_write('test overwrite', '/default/file'))
        mock_print.assert_any_call('Overwrite this file?')
        mock_print.mock_reset()

        # test case 3
        self.assertEqual('/path/to/file4', input_path_for_write('test open error', '/default/file'))
        mock_print.assert_any_call('Error: can not write to this file.')
        mock_print.mock_reset()

        # test case 4
        self.assertEqual('/default/file', input_path_for_write('test default', '/default/file'))
        mock_print.mock_reset()
        