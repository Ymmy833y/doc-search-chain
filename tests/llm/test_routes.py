import unittest
from unittest.mock import patch
from app import create_app
from app.llm.services import Model
from app.llm.errors import NoReadableDocumentsError

class LlmRoutesTestCase(unittest.TestCase):
  
  def setUp(self):
    self.app = create_app()
    self.app.config['TESTING'] = True
    self.client = self.app.test_client()

  def test_model_build_success(self):
    with patch.object(Model, 'build') as mock_build:
      mock_build.return_value = None

      response = self.client.get('/llm/modelBuild')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.data.decode(), "Model built successfully")
      mock_build.assert_called_once()

  def test_model_build_failure(self):
    with patch.object(Model, 'build') as mock_build:

      mock_build.side_effect = NoReadableDocumentsError('No readable documents were found.')
      response = self.client.get('/llm/modelBuild')
      self.assertEqual(response.status_code, 500)
      self.assertIn("No readable documents were found.", response.data.decode())
      mock_build.assert_called_once()

  @patch.object(Model, 'valid_get_answer')
  @patch.object(Model, 'get_answer')
  def test_search_success(self, mock_get_answer, mock_valid_get_answer):
    mock_get_answer.return_value = iter(["answer"])
    
    response = self.client.get('/llm/search?input=test')
    
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data.decode(), "answer")
    mock_valid_get_answer.assert_called_once()
    mock_get_answer.assert_called_once_with("test")

  @patch.object(Model, 'valid_get_answer')
  @patch.object(Model, 'get_answer')
  def test_search_failure(self, mock_get_answer, mock_valid_get_answer):
    mock_valid_get_answer.side_effect = NameError("The model has not been built.")
    
    response = self.client.get('/llm/search?input=test')
    
    self.assertEqual(response.status_code, 500)
    self.assertIn("The model has not been built.", response.data.decode())
    mock_valid_get_answer.assert_called_once()
    mock_get_answer.assert_not_called()


if __name__ == '__main__':
  unittest.main()
