from flask import Response, request
import logging
from . import llm
from .services import Model

model = Model()

@llm.route('/modelBuild')
def model_build():
  logging.info('[llm] model build is called.')
  try:
    model.build()
    return Response("Model built successfully", status=200, content_type='text/plain')
  except Exception as e:
    logging.error(f"Error: {str(e)}")
    return Response(str(e), status=500, content_type='text/plain')

@llm.route('/search')
def search():
  logging.info('[llm] search is called.')
  try:
    input = request.args.get('input')
    model.valid_get_answer()
    answer = model.get_answer(input)
    return Response(answer, status=200, content_type='text/event-stream')
  except Exception as e:
    logging.error(f"Error: {str(e)}")
    return Response(str(e), status=500, content_type='text/plain')
