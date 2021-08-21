from _common import render_bash, get_server_directory
import os


def main():
    server_dir = get_server_directory()

    folder = os.path.join(server_dir, 'Scripts')
    if not os.path.exists(folder):
        os.mkdir(folder)

    render_bash('dependency-installer', os.path.join(folder, 'dependency-installer.sh'), dict(
        dir=server_dir,
    ))

    render_bash('updater', os.path.join(folder, 'updater.sh'), dict(
        dir=server_dir,
    ))

    render_bash('cert-maker', os.path.join(folder, 'certmaker.sh'), dict(
        dir=os.path.join(server_dir, 'Gun', 'ssl'),
    ))

    render_bash('service-maker', os.path.join(folder, 'service-maker.sh'), dict(
        dir=server_dir,
    ))

    render_bash('service-enabler', os.path.join(folder, 'service-enabler.sh'))

    render_bash('service-disabler', os.path.join(folder, 'service-disabler.sh'))

    render_bash('service-starter', os.path.join(folder, 'service-starter.sh'))

    render_bash('service-stopper', os.path.join(folder, 'service-stopper.sh'))

    render_bash('process-starter', os.path.join(folder, 'process-starter.sh'), dict(
        dir=server_dir,
    ))

    render_bash('process-killer', os.path.join(folder, 'process-killer.sh'), dict(
        dir=server_dir,
    ))


if __name__ == '__main__':
    main()
