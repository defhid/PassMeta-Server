from App import app


if __name__ == '__main__':
    import uvicorn

    app.debug = True

    # noinspection PyTypeChecker
    uvicorn.run(app, host="127.0.0.1", port=8000)
