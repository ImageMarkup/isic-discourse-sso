def create_app(config: Optional[dict] = None) -> Flask:
    config = config or {}

    # build/configure app
    app = Flask(__name__)
    app.config.update(config)

    # register blueprints
    app.register_blueprint(file_bp, url_prefix=f"/{app.config['API_PATH']}/file")

    # register error handlers
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(HTTPError, handle_http_error)
    app.register_error_handler(RequestError, handle_request_error)
    # ensure all errors are masked as 500 in production
    if app.config["ENV"] == "production":
        app.register_error_handler(Exception, handle_general_error)

    return app
