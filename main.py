from App import app


if __name__ == '__main__':
    import uvicorn
    import logging

    # noinspection PyTypeChecker
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level=logging.INFO)
