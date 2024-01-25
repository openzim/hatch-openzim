from __future__ import annotations

from hatchling.metadata.plugin.interface import MetadataHookInterface

from hatch_openzim.metadata import update


class OpenzimMetadataHook(MetadataHookInterface):
    """Hatch metadata hook to populate 'project' data

    This hook populates:
    - project urls
    """

    PLUGIN_NAME = "openzim-metadata"

    def update(self, metadata: dict):
        """Update the project table's metadata."""
        update(root=self.root, config=self.config, metadata=metadata)
