import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import urlopen

try:
    import tomllib  # pyright: ignore[reportMissingTypeStubs]
except ImportError:  # pragma: no cover
    import toml as tomllib

from hatch_openzim.shared import logger

DEFAULT_OPENZIM_TOML_LOCATION = "openzim.toml"


def process(openzim_toml_location: str = DEFAULT_OPENZIM_TOML_LOCATION):
    """performs openZIM operations on files, i.e. download and extract ZIPs

    Configuration is read from openzim.toml which must be in root of the hatch project,
    next to pyproject.toml

    openzim_toml_location: location of the openzim.toml file with instructions about
    files to install locally
    """
    config_path = Path(openzim_toml_location)
    if not config_path.exists():
        if openzim_toml_location != DEFAULT_OPENZIM_TOML_LOCATION:
            raise Exception(f"File is missing at {openzim_toml_location}")
        else:
            return
    config = tomllib.loads(config_path.read_text())
    files_config = config.get("files", None)
    if not files_config:
        return

    for section_name, section_data in files_config.items():
        _process_section(section_name=section_name, section_data=section_data)


def _process_section(section_name: str, section_data: Dict[str, Any]):
    """processes all actions required for one section (i.e. one target folder)"""

    logger.info(f"Processing {section_name} section")
    section_config = section_data.get("config", None)
    if not section_config:
        raise Exception("config table is mandatory")
    base_target_dir = section_config.get("target_dir", None)
    if not base_target_dir:
        raise Exception("target_dir is mandatory in config table")
    base_target_dir = Path(base_target_dir)
    section_actions = section_data.get("actions", None)
    if not section_actions:
        logger.info("  No actions to process")
        return
    base_target_dir = Path(section_config["target_dir"])
    base_target_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"  Installing files in {base_target_dir}")
    for action_name, action_config in section_actions.items():
        _process_one_action(base_target_dir, action_name, action_config)

    execute_after = section_config.get("execute_after", None)
    if execute_after:
        _process_execute_after(base_target_dir=base_target_dir, actions=execute_after)

    logger.info(" All done")


def _process_one_action(
    base_target_dir: Path, action_name: str, action_data: Dict[str, Any]
):
    """processes one action (basically trigger the right kind of action)"""
    logger.info(f"  Processing {action_name} action")
    source = action_data.get("source", None)
    if not source:
        raise Exception("source is not configured")
    action = action_data.get("action", None)
    if not action:
        raise Exception("action is not configured")

    if action == "get_file":
        _process_get_file_action(
            base_target_dir=base_target_dir, source=source, action_data=action_data
        )

    elif action == "extract_all":
        _process_extract_all_action(
            base_target_dir=base_target_dir, source=source, action_data=action_data
        )

    elif action == "extract_items":
        _process_extract_items_action(
            base_target_dir=base_target_dir, source=source, action_data=action_data
        )

    else:
        raise Exception(f"Unsupported action '{action}'")

    execute_after = action_data.get("execute_after", None)
    if execute_after:
        _process_execute_after(base_target_dir=base_target_dir, actions=execute_after)

    logger.info("    Done")


def _process_execute_after(base_target_dir: Path, actions: List[str]):
    """execute actions after file(s) installation"""

    for action in actions:
        logger.info(f"    Executing '{action}'")
        process = subprocess.run(
            action,
            shell=True,  # noqa: S602 # nosec: B602
            cwd=base_target_dir,
            text=True,
            check=True,
            capture_output=True,
        )
        if process.stdout:
            logger.info(f"      stdout:\n{process.stdout}")


def _process_get_file_action(
    base_target_dir: Path, source: str, action_data: Dict[str, Any]
):
    """downloads one file to a given location"""
    target_file = action_data.get("target_file", None)
    if not target_file:
        raise Exception("target_file is mandatory when action='get_file'")
    target_dir = action_data.get("target_dir", None)
    local_dir = base_target_dir
    if target_dir:
        local_dir = base_target_dir / str(target_dir)
        local_dir.mkdir(parents=True, exist_ok=True)
    local_file = local_dir / str(target_file)
    if local_file.exists():
        logger.info("    Skipping, local_file is already present")
        return
    _download_file(source, local_file)


def _process_extract_all_action(
    base_target_dir: Path, source: str, action_data: Dict[str, Any]
):
    """extacts all Zip content to a given location

    Supports the remove attribute which allows to delete some Zip content
    """
    target_dir = action_data.get("target_dir", None)
    if not target_dir:
        raise Exception("target_dir is mandatory when action='extract_all'")
    target_dir = base_target_dir / str(target_dir)
    if target_dir.exists():
        logger.info("    Skipping, target_dir is already present")
        return
    if not target_dir.parent.exists():
        target_dir.parent.mkdir(parents=True, exist_ok=True)
    _extract_zip_from_url(url=source, extract_to=target_dir)
    if "remove" in action_data:
        _remove_items(globs=action_data["remove"], directory=target_dir)


def _process_extract_items_action(
    base_target_dir: Path, source: str, action_data: Dict[str, Any]
):
    """extacts some items of a content to some given locations

    Supports the remove attribute which allows to delete some items content after
    extraction
    """
    zip_paths = action_data.get("zip_paths", None)
    if not zip_paths:
        raise Exception("zip_paths is mandatory when action='extract_items'")
    target_paths = action_data.get("target_paths", None)
    if not target_paths:
        raise Exception("target_paths is mandatory when action='extract_items'")
    if len(zip_paths) != len(target_paths):
        raise Exception(
            f"zip_paths and target_paths must have same length ({len(zip_paths)} !="
            f" {len(target_paths)})"
        )

    # do not re-install if asset has already been installed
    if any(
        (base_target_dir / str(target_path)).exists() for target_path in target_paths
    ):
        logger.info("    Skipping, at least one target path is already present")
        return

    with tempfile.TemporaryDirectory() as tempdir:
        tempath = Path(tempdir)
        _extract_zip_from_url(url=source, extract_to=tempath)
        for index, zip_path in enumerate(zip_paths):
            item_src = tempath / str(zip_path)
            item_dst = base_target_dir / str(target_paths[index])
            if item_dst.parent and not item_dst.parent.exists():
                item_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src=str(item_src), dst=item_dst)

    if "remove" in action_data:
        _remove_items(globs=action_data["remove"], directory=base_target_dir)


def _remove_items(directory: Path, globs: List[str]):
    """removes all files in directory matching one of the provided glob patterns"""
    for pattern in globs:
        matches = directory.glob(pattern)
        for match in matches:
            if match.is_file():
                match.unlink()
            elif match.is_dir():  # pragma: no branch
                shutil.rmtree(match)


def _download_file(url: str, download_to: Path):
    """downloads a file to a given location"""
    if not url.startswith(("http:", "https:")):
        raise ValueError("URL must start with 'http:' or 'https:'")
    with urlopen(url) as response, open(download_to, "wb") as file:  # noqa: S310
        file.write(response.read())


def _extract_zip_from_url(url: str, extract_to: Path):
    """downloads ZIP from URL and extract in given directory

    Nota: the ZIP is temporarily saved on disk (there is no convenient function
    to stream the web resource to the ZIP extractor in Python standard library)
    """

    if not url.startswith(("http:", "https:")):
        raise ValueError("URL must start with 'http:' or 'https:'")
    with urlopen(url) as response:  # noqa: S310
        with tempfile.NamedTemporaryFile(delete=False) as temp_zip:
            shutil.copyfileobj(response, temp_zip)
        with zipfile.ZipFile(temp_zip.name, "r") as zip_file:
            zip_file.extractall(extract_to)
        Path(temp_zip.name).unlink()
