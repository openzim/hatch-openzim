from hatchling.plugin import hookimpl

from hatch_openzim.build_hook import OpenzimBuildHook
from hatch_openzim.metadata_hook import OpenzimMetadataHook


@hookimpl
def hatch_register_build_hook() -> type[OpenzimBuildHook]:
    return OpenzimBuildHook


@hookimpl
def hatch_register_metadata_hook() -> type[OpenzimMetadataHook]:
    return OpenzimMetadataHook
