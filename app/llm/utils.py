from enum import Enum
from langchain_text_splitters import Language
from langchain_community import document_loaders as loaders

class LanguageExtension(Enum):
  """Enum of file extensions associated with languages and loaders."""
  
  # C = ("c", Language.C, loaders.TextLoader) is not implemented
  CPP = ("cpp", Language.CPP, loaders.TextLoader)
  CC = ("cc", Language.CPP, loaders.TextLoader)
  CXX = ("cxx", Language.CPP, loaders.TextLoader)
  HPP = ("hpp", Language.CPP, loaders.TextLoader)
  HXX = ("hxx", Language.CPP, loaders.TextLoader)
  H = ("h", Language.CPP, loaders.TextLoader)
  GO = ("go", Language.GO, loaders.TextLoader)
  JAVA = ("java", Language.JAVA, loaders.TextLoader)
  KT = ("kt", Language.KOTLIN, loaders.TextLoader)
  KTS = ("kts", Language.KOTLIN, loaders.TextLoader)
  JS = ("js", Language.JS, loaders.TextLoader)
  TS = ("ts", Language.TS, loaders.TextLoader)
  PHP = ("php", Language.PHP, loaders.TextLoader)
  PROTO = ("proto", Language.PROTO, loaders.TextLoader)
  PY = ("py", Language.PYTHON, loaders.PythonLoader)
  RST = ("rst", Language.RST, loaders.TextLoader)
  RB = ("rb", Language.RUBY, loaders.TextLoader)
  RS = ("rs", Language.RUST, loaders.TextLoader)
  SCALA = ("scala", Language.SCALA, loaders.TextLoader)
  SC = ("sc", Language.SCALA, loaders.TextLoader)
  SWIFT = ("swift", Language.SWIFT, loaders.TextLoader)
  MD = ("md", Language.MARKDOWN, loaders.UnstructuredMarkdownLoader)
  TEX = ("tex", Language.LATEX, loaders.TextLoader)
  HTML = ("html", Language.HTML, loaders.UnstructuredHTMLLoader)
  HTM = ("htm", Language.HTML, loaders.UnstructuredHTMLLoader)
  SOL = ("sol", Language.SOL, loaders.TextLoader)
  CS = ("cs", Language.CSHARP, loaders.TextLoader)
  COB = ("cob", Language.COBOL, loaders.TextLoader)
  CBL = ("cbl", Language.COBOL, loaders.TextLoader)
  LUA = ("lua", Language.LUA, loaders.TextLoader)
  # PL =("pl", Language.PERL, loaders.TextLoader) is not implemented
  HS = ("hs", Language.HASKELL, loaders.TextLoader)
  EX = ("ex", Language.ELIXIR, loaders.TextLoader)
  EXS = ("exs", Language.ELIXIR, loaders.TextLoader)

  def __init__(self, extension, language, loader):
    self.extension = extension
    self.language = language
    self.loader = loader

  @staticmethod
  def get_extension(ext: str):
    for lang_ext in LanguageExtension:
      if lang_ext.extension == ext:
        return lang_ext
    return None

  @staticmethod
  def get_language(ext: str):
    lang_ext = LanguageExtension.get_extension(ext)
    return lang_ext.language if lang_ext else False

  @staticmethod
  def get_loader(ext: str):
    lang_ext = LanguageExtension.get_extension(ext)
    return lang_ext.loader if lang_ext else False

