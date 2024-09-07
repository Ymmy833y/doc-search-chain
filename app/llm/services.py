import os
import json
from .errors import NoReadableDocumentsError

from flask import current_app

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.documents.base import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, HTMLSectionSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PDFMinerLoader
from langchain_chroma import Chroma
from uuid import uuid4

class Model:
  def __init__(self):
    self.__rag_chain = None
  
  def build(self):
    os.environ['OPENAI_API_KEY'] = get_api_key()

    docs = self.__doc_loader()
    uuids = [str(uuid4()) for _ in range(len(docs))]

    vectorstore = Chroma(
      collection_name="example_collection",
      embedding_function=OpenAIEmbeddings()
    )
    vectorstore.add_documents(documents=docs, ids=uuids)
    retriever = vectorstore.as_retriever(
      search_type="mmr", search_kwargs={"k": 1, "fetch_k": 5}
    )

    custom_rag_prompt = PromptTemplate.from_template(get_template())
    
    llm = ChatOpenAI(model="gpt-4o-mini")

    self.__rag_chain = (
      {"context": retriever | format_docs, "question": RunnablePassthrough()}
      | custom_rag_prompt
      | llm
      | StrOutputParser()
    )

  def get_answer(self, input):
    try:
      for chunk in self.__rag_chain.stream(input):
        yield chunk
    except Exception as e:
      yield f"Error: {str(e)}"

  def valid_get_answer(self):
    if self.__rag_chain == None:
      raise NameError("The model has not been built.")


  def __doc_loader(self):
    docs = self.__doc_loader_for_md() + self.__doc_loader_for_pdf() + self.__doc_loader_for_general()
    if len(docs) <= 0:
      raise NoReadableDocumentsError('No readable documents were found.')
    return docs

  def __doc_loader_for_md(self):
    loader = DirectoryLoader(
      current_app.config["DOCS_FOLDER"], glob="**/*.md", 
      silent_errors=True, loader_cls=TextLoader
    )
    docs = loader.load()
    text_splitter = MarkdownHeaderTextSplitter([
      ("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"),
    ])
    return text_splitter.split_text("\n\n".join([d.page_content for d in docs]))

  def __doc_loader_for_pdf(self):
    loader = DirectoryLoader(
      current_app.config["DOCS_FOLDER"], glob="**/*.pdf", 
      silent_errors=True, loader_cls=PDFMinerLoader
    )
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200,
      length_function=len,
    )
    return text_splitter.split_documents(docs)

  def __doc_loader_for_general(self):
    loader = DirectoryLoader(
      current_app.config["DOCS_FOLDER"], exclude=["**/*.md", "**/*.pdf"], 
      silent_errors=True, loader_cls=TextLoader
    )
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200,
      length_function=len,
    )
    return text_splitter.split_documents(docs)


def get_template():
  template = """Use the following pieces of context to answer the question at the end.
  If you don't know the answer, just say that you don't know, don't try to make up an answer.
  When replying, please translate into {language}.

  {context}

  Question: {question}

  Helpful Answer:"""
  return template.format(language=get_default_language(), context="{context}", question="{question}")

def format_docs(docs: list[Document]):
  return "\n\n".join(doc.page_content for doc in docs)

def get_api_key():
  with open(current_app.config["CONFIG_FILE"], "r") as file:
    config = json.load(file)
    return config["api_key"]

def get_default_language():
  with open(current_app.config["CONFIG_FILE"], "r") as file:
    config = json.load(file)
    return config["default_language"]
