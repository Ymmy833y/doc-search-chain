import os
import unittest
from unittest.mock import patch
from app import create_app

class AppRoutesTestCase(unittest.TestCase):
  
  def setUp(self):
    self.app = create_app()
    self.app.config['TESTING'] = True
    self.app.config['DOCS_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs'))
    self.app.config['CONFIG_FILE'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config.json'))
    self.client = self.app.test_client()
      
  def test_index(self):
    response = self.client.get('/')
    self.assertEqual(response.status_code, 200)
          
  def test_setting_form(self):
    with patch('app.main.routes.update_setting') as mock_update_setting:

      response = self.client.post('/settingForm', data={"default_language": "English", "theme": "light", "api_key": "dumy"})
      self.assertEqual(response.status_code, 302)

      mock_update_setting.assert_called_once()
      called_args = mock_update_setting.call_args[0][0]

      self.assertEqual(dict(called_args), {"default_language": "English", "theme": "light", "api_key": "dumy"})

  def test_search_form(self):
    response = self.client.post('/searchForm', json={'input': 'test_search'})
    self.assertEqual(response.status_code, 302)
    self.assertIn('/llm/search?input=test_search', response.headers['Location'])

  def test_load_document_success(self):
    with patch('app.main.routes.valid_load_document') as mock_valid_load_document, \
      patch('app.main.routes.get_docs') as mock_get_docs, \
      patch('app.llm.routes.model.build') as mock_model_build:

      mock_get_docs.return_value = ['doc1.txt']
      mock_valid_load_document.return_value = None
      mock_model_build.return_value = None
      
      response = self.client.post('/loadDocument')
      self.assertEqual(response.status_code, 302)
      self.assertIn('/llm/modelBuild', response.headers['Location'])

  def test_load_document_failure(self):
    with patch('app.main.routes.valid_load_document') as mock_valid_load_document:
      mock_valid_load_document.side_effect = NameError("Document to be loaded does not exist.")

      response = self.client.post('/loadDocument')
      self.assertEqual(response.status_code, 500)
      self.assertIn(b'Document to be loaded does not exist.', response.data)


  def test_load_document_success(self):
    with patch('app.main.routes.valid_load_document') as mock_valid_load_document, \
      patch('app.main.routes.get_docs') as mock_get_docs:
      
      mock_get_docs.return_value = ['doc1.txt']
      mock_valid_load_document.return_value = None
      
      response = self.client.post('/loadDocument')
      self.assertEqual(response.status_code, 302)
      self.assertIn('/llm/modelBuild', response.headers['Location'])

  def test_remove_form(self):
    with patch('app.main.routes.remove_file') as mock_remove_file:
      response = self.client.post('/removeForm', data={'file1.txt': 'value'})
      self.assertEqual(response.status_code, 302)

      mock_remove_file.assert_called_once()
      called_args = mock_remove_file.call_args[0][0]
      self.assertEqual(dict(called_args), {'file1.txt': 'value'})


if __name__ == '__main__':
  unittest.main()
