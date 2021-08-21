def before_load():
    from App.settings import load_custom_settings
    import app_settings

    load_custom_settings(app_settings)


before_load()


if __name__ == '__main__':
    from App.controllers import app
    import uvicorn
    import logging

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level=logging.INFO)
else:
    from App.controllers import app
