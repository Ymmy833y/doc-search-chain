from flask import Response, redirect, render_template, url_for, request
import logging
from . import main
from .services import get_docs, get_setting, update_setting, valid_load_document, upload_file, remove_file

@main.route('/')
def index():
  files = get_docs()
  setting = get_setting()
  select_tab = request.args.get('select_tab', 'search')
  return render_template('index.html', files=files, setting=setting, select_tab=select_tab)

@main.route('/settingForm', methods=['POST'])
def setting_form():
  logging.info('[main] setting form is called.')
  update_setting(request.form)
  return redirect(url_for('.index'))

@main.route('/searchForm', methods=['POST'])
def search_form():
  logging.info('[main] search form is called.')
  input = request.json.get('input')
  return redirect(url_for('llm.search', input=input))

@main.route('/loadDocument', methods=['POST'])
def load_document():
  logging.info('[main] load document is called.')
  try:
    valid_load_document()
    return redirect(url_for('llm.model_build'))
  except Exception as e:
    logging.error(f"Error: {str(e)}")
    return Response(str(e), status=500, content_type='text/plain')

@main.route('uploadForm', methods=['POST'])
def upload_form():
  logging.info('[main] upload form is called.')
  upload_file(request.files)
  return redirect(url_for('.index', select_tab="document"))

@main.route('removeForm', methods=['POST'])
def remove_form():
  logging.info('[main] remove form is called.')
  remove_file(request.form)
  return redirect(url_for('.index', select_tab="document"))
