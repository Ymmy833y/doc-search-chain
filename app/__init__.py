from flask import Flask

def create_app():
  app = Flask(__name__, template_folder="../templates", static_folder="../static")
  
  # Configuration
  app.config.from_object('app.config.Config')

  # Register Blueprints
  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint, url_prefix='/')
  
  from .llm import llm as llm_blueprint
  app.register_blueprint(llm_blueprint, url_prefix='/llm')

  return app
