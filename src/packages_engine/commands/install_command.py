from packages_engine.services.installer import InstallerServiceContract
from packages_engine.services.installer.installer_tasks import InstallerTask


class InstallCommand:
    def __init__(self, installer: InstallerServiceContract,
                 install_tasks: list[InstallerTask]):
        self.installer = installer
        self.install_tasks = install_tasks

    def execute(self):
        self.installer.install(self.install_tasks)
