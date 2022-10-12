from App.settings import load_custom_settings
import app_settings

load_custom_settings(app_settings)


if __name__ == '__main__':
    from App.app import app
    import uvicorn
    import logging

    uvicorn.run(app, host="127.0.0.1", port=80, log_level=logging.INFO)
else:
    from App.app import app
