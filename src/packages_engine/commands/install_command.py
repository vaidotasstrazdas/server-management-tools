from packages_engine.services.package_controller import PackageControllerServiceContract

class InstallCommand:
    controller: PackageControllerServiceContract

    def __init__(self, controller: PackageControllerServiceContract):
        self.controller = controller

    def execute(self):
        self.controller.install_package("wireguard")
        self.controller.install_package("dnsmasq")
        self.controller.install_package("nftables")
        self.controller.install_package("ca-certificates")
        self.controller.install_package("curl")
        self.controller.install_package("gnupg")