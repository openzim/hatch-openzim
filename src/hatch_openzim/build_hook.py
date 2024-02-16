from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_openzim.files_install import process as process_files_install


class OpenzimBuildHook(
    BuildHookInterface  # pyright: ignore[reportMissingTypeArgument]
):
    """Hatch build hook to perform custom openzim actions

    This hook performs:
    - files installation
    """

    PLUGIN_NAME = "openzim-build"

    def initialize(self, version: str, build_data: Dict[str, Any]):  # noqa: ARG002
        if "toml-config" in self.config:
            process_files_install(openzim_toml_location=self.config["toml-config"])
        else:
            process_files_install()
