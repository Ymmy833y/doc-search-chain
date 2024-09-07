import os
import json
import logging

from flask import current_app
from werkzeug.datastructures import ImmutableMultiDict, FileStorage

def get_docs():
  return os.listdir(current_app.config["DOCS_FOLDER"])

def get_setting():
  with open(current_app.config["CONFIG_FILE"], "r") as file:
    return json.load(file)

def update_setting(data: ImmutableMultiDict[str, str]):
  with open(current_app.config["CONFIG_FILE"], 'w') as file:
    json.dump(data, file)

def valid_load_document():
  if len(get_docs()) <= 0:
    raise NameError("Document to be loaded does not exist.")

def upload_file(files: ImmutableMultiDict[str, FileStorage]):  
  if 'docs' not in files:
    logging.info('The file to upload does not exist.')
    return
  for file in files.getlist('docs'):
    if file.filename != '':
      file.save(os.path.join(current_app.config['DOCS_FOLDER'], file.filename))

def remove_file(files: ImmutableMultiDict[str, str]):
  for file in files.keys():
    file_path = os.path.join(current_app.config['DOCS_FOLDER'], file)
    if os.path.exists(file_path):
      os.remove(file_path)
    else:
      logging.info(f"{file} not found.")
