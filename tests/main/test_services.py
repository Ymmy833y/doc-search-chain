import os
import unittest
from unittest.mock import MagicMock, mock_open, patch
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from app import create_app
from app.main.services import get_docs, get_setting, update_setting, valid_load_document, upload_file, remove_file

class AppServicesTestCase(unittest.TestCase):
  
  def setUp(self):
    self.app = create_app()
    self.app.config['TESTING'] = True
    self.app.config['DOCS_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs'))
    self.app.config['CONFIG_FILE'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config.json'))
    self.client = self.app.test_client()

  @patch('app.main.services.os.listdir')
  def test_get_docs(self, mock_listdir):
    mock_listdir.return_value = ['file1.txt', 'file2.pdf', 'file3.docx']

    with self.app.app_context():
      result = get_docs()
      self.assertEqual(result, ['file1.txt', 'file2.pdf', 'file3.docx'])
  
    mock_listdir.assert_called_once_with(self.app.config['DOCS_FOLDER'])


  @patch('builtins.open', new_callable=mock_open, read_data='{"setting_key": "setting_value"}')
  @patch('json.load')
  def test_get_setting(self, mock_json_load, mock_open):
    mock_json_load.return_value = {"setting_key": "setting_value"}

    with self.app.app_context():
      result = get_setting()
      self.assertEqual(result, {"setting_key": "setting_value"})

    mock_open.assert_called_once_with(self.app.config['CONFIG_FILE'], 'r')
    mock_json_load.assert_called_once()

  @patch('builtins.open', new_callable=mock_open)
  @patch('json.dump')
  def test_update_setting(self, mock_json_dump, mock_open):
    test_data = ImmutableMultiDict([('setting_key', 'setting_value')])

    with self.app.app_context():
      update_setting(test_data)

    mock_open.assert_called_once_with(self.app.config['CONFIG_FILE'], 'w')
    mock_json_dump.assert_called_once_with(test_data, mock_open())

  @patch('app.main.services.get_docs')
  def test_valid_load_document_raises_name_error(self, mock_get_docs):
    mock_get_docs.return_value = []

    with self.assertRaises(NameError) as context:
      valid_load_document()

    self.assertEqual(str(context.exception), "Document to be loaded does not exist.")

  @patch('app.main.services.get_docs')
  def test_valid_load_document_passes_with_docs(self, mock_get_docs):
    mock_get_docs.return_value = ['file1.txt']

    try:
      valid_load_document()
    except NameError:
      self.fail("valid_load_document() raised NameError unexpectedly!")

  @patch('app.main.services.os.path.join', return_value='/docs/file1.txt')
  def test_upload_file_with_valid_file(self, mock_join):
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = 'file1.txt'

    files = ImmutableMultiDict([('docs', mock_file)])

    with self.app.app_context():
      upload_file(files)

    mock_join.assert_called_once_with(self.app.config['DOCS_FOLDER'], 'file1.txt')

  @patch('app.main.services.logging.info')
  def test_upload_file_without_docs_key(self, mock_logging_info):
    files = ImmutableMultiDict()

    with self.app.app_context():
      upload_file(files)

    mock_logging_info.assert_called_once_with('The file to upload does not exist.')

  @patch('app.main.services.FileStorage.save')
  def test_upload_file_with_empty_filename(self, mock_save):
    mock_file = MagicMock(spec=FileStorage)
    mock_file.filename = ''

    files = ImmutableMultiDict([('docs', mock_file)])

    with self.app.app_context():
      upload_file(files)

    mock_save.assert_not_called()

  @patch('app.main.services.os.path.exists')
  @patch('app.main.services.os.remove')
  def test_remove_file_with_existing_file(self, mock_remove, mock_exists):
    mock_exists.return_value = True
    files = ImmutableMultiDict([('file1.txt', 'dummy')])

    with self.app.app_context():
      remove_file(files)

    mock_exists.assert_called_once_with(os.path.join(self.app.config['DOCS_FOLDER'], 'file1.txt'))
    mock_remove.assert_called_once_with(os.path.join(self.app.config['DOCS_FOLDER'], 'file1.txt'))

  @patch('app.main.services.os.path.exists')
  @patch('app.main.services.logging.info')
  def test_remove_file_with_non_existing_file(self, mock_logging_info, mock_exists):
    mock_exists.return_value = False
    files = ImmutableMultiDict([('file2.txt', 'dummy')])

    with self.app.app_context():
      remove_file(files)

    mock_exists.assert_called_once_with(os.path.join(self.app.config['DOCS_FOLDER'], 'file2.txt'))
    mock_logging_info.assert_called_once_with('file2.txt not found.')

  @patch('app.main.services.os.path.exists')
  @patch('app.main.services.os.remove')
  def test_remove_file_with_multiple_files(self, mock_remove, mock_exists):
    mock_exists.side_effect = [True, False]
    files = ImmutableMultiDict([('file1.txt', 'dummy1'), ('file2.txt', 'dummy2')])

    with self.app.app_context():
      remove_file(files)

    mock_exists.assert_any_call(os.path.join(self.app.config['DOCS_FOLDER'], 'file1.txt'))
    mock_exists.assert_any_call(os.path.join(self.app.config['DOCS_FOLDER'], 'file2.txt'))
    mock_remove.assert_called_once_with(os.path.join(self.app.config['DOCS_FOLDER'], 'file1.txt'))


if __name__ == '__main__':
  unittest.main()
