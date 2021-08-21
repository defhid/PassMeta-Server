import os


def __render(templates_dir: str, template_name: str, filepath_to: str, params: dict[str, str] = None):
    try:
        with open(os.path.join('templates', templates_dir, template_name + '.template'), 'r') as t:
            result = t.read()
    except Exception:
        print(f"Error occurred during import '{template_name}.template'!")
        raise

    try:
        with open(filepath_to, 'wb') as file:
            file.write(result.format(
                **(params if params else {}),
                gun_service_name=GUN_SERVICE_NAME,
            ).encode("utf-8"))
    except Exception:
        print(f"Error occurred during writing template '{template_name}'!")
        raise


def render_config(template_name: str, filepath_to: str, params: dict[str, str] = None):
    return __render('config', template_name, filepath_to, params)


def render_bash(template_name: str, filepath_to: str, params: dict[str, str] = None):
    return __render('bash', template_name, filepath_to, params)


def render_etc(template_name: str, filepath_to: str, params: dict[str, str] = None):
    return __render('etc', template_name, filepath_to, params)


def get_server_directory() -> str:
    return os.path.split(os.path.split(__file__)[0])[0]


GUN_SERVICE_NAME = "passmeta-server-app"
