import os
import unittest
from unittest.mock import MagicMock, patch
from app import create_app
from app.llm.services import Model
from app.llm.errors import NoReadableDocumentsError
from langchain_core.documents.base import Document

class LlmServicesTestCase(unittest.TestCase):

  def setUp(self):     
    self.app = create_app()
    self.app.config['TESTING'] = True
    self.app.config['DOCS_FOLDER'] = os.path.join(os.path.dirname(__file__), '../docs')
    self.app.config['CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), '../config.json')
    self.app_context = self.app.app_context()
    self.app_context.push()

  @patch('app.llm.services.Chroma')
  @patch('app.llm.services.ChatOpenAI')
  @patch('app.llm.services.Model._Model__doc_loader')
  def test_build_succes(self, mock_chat_openai, mock_chroma, mock_doc_loader):    
    mock_vectorstore = MagicMock()
    mock_chroma.return_value = mock_vectorstore
    mock_retriever = MagicMock()
    mock_vectorstore.as_retriever.return_value = mock_retriever
    mock_doc_loader = [Document("doc1"), Document("doc2")]
    
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    model = Model()
    model.build()

    mock_chroma.assert_called_once_with(model='gpt-4o-mini')
    mock_chat_openai.assert_called_once_with()

  @patch('app.llm.services.Model._Model__doc_loader')
  def test_build_failure(self, mock_doc_loader):
    mock_doc_loader.side_effect = NoReadableDocumentsError('No readable documents were found.')

    model = Model()
    with self.assertRaises(NoReadableDocumentsError):
        model.build()

  def test_get_answer_success(self):
    model = Model()
    model._Model__rag_chain = MagicMock()
    model._Model__rag_chain.stream.return_value = iter(["chunk1", "chunk2", "chunk3"])
    
    result = list(model.get_answer("Test input"))
    self.assertEqual(result, ["chunk1", "chunk2", "chunk3"])

  def test_get_answer_failure(self):
    model = Model()
    model._Model__rag_chain = MagicMock()
    model._Model__rag_chain.stream.side_effect = Exception("Test exception")

    result = list(model.get_answer("Test input"))
    self.assertEqual(result, ["Error: Test exception"])

  def test_valid_get_answer_with_none_rag_chain(self):
    model = Model()
    with self.assertRaises(NameError) as context:
      model.valid_get_answer()
    
    self.assertEqual(str(context.exception), "The model has not been built.")

  def test_valid_get_answer_with_valid_rag_chain(self):
    model = Model()
    model._Model__rag_chain = "dummy_chain"
    
    try:
      model.valid_get_answer()
    except NameError:
      self.fail("valid_get_answer() raised NameError unexpectedly!")


if __name__ == '__main__':
    unittest.main()
