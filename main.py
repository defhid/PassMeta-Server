def before_load():
    from App.settings import load_private_settings
    import private_settings

    load_private_settings(private_settings)


before_load()


if __name__ == '__main__':
    from App.controllers import app
    import uvicorn
    import logging

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level=logging.INFO)
else:
    from App.controllers import app
