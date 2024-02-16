import os
import subprocess
import tempfile
from pathlib import Path
from typing import List

import pytest

from hatch_openzim import files_install


@pytest.fixture
def nominal_files():
    return [
        "part1/action1/file1.txt",
        "part1/action1/file2.txt",
        "part1/action1/keep1/file1.txt",
        "part1/action1/keep1/file2.txt",
        "part1/action1/remove3/file2.txt",
        "part1/somewhere/something.txt",
        "part1/somewhere_else/something.txt",
        "part2/file123.txt",
        "part2/action5/subfolder1/file123.txt",
        "part2/action2/file1.txt",
        "part2/action2/file2.txt",
        "part2/action3/file1.json",
        "part2/action3/file1.txt",
        "part2/action3/file2.json",
        "part2/action3/file2.txt",
        "part4/action2/file4.txt",
        "part4/file4.txt",
        "part4/subdir1/action3/file1.txt",
        "part4/subdir1/action3/file2.txt",
        "part4/subdir1/action3/keep1/file1.txt",
        "part4/subdir1/action3/keep1/file2.txt",
        "part4/subdir1/action3/remove1/file1.txt",
        "part4/subdir1/action3/remove1/file2.txt",
        "part4/subdir1/action3/remove2.txt",
        "part4/subdir1/action3/remove3/file1.txt",
        "part4/subdir1/action3/remove3/file2.txt",
    ]


def test_no_arg():
    """Test default case where no config is passed and file is missing"""
    files_install.process()


@pytest.mark.parametrize(
    "config_file",
    [
        ("empty.toml"),
        ("other_stuff.toml"),
    ],
)
def test_ignored_silently(config_file: str):
    """Test cases where the config file is passed but there is no relevant content"""
    files_install.process(
        str((Path(__file__).parent / "configs" / config_file).absolute())
    )


@pytest.mark.parametrize(
    "config_file, exception_message",
    [
        ("i_m_not_here.toml", "File is missing at .*/i_m_not_here.toml"),
        ("missing_config.toml", "config table is mandatory"),
        ("missing_target_dir.toml", "target_dir is mandatory in config table"),
        ("missing_source.toml", "source is not configured"),
        ("missing_action.toml", "action is not configured"),
        (
            "get_file_missing_target_file.toml",
            "target_file is mandatory when action='get_file'",
        ),
        (
            "extract_all_missing_target_dir.toml",
            "target_dir is mandatory when action='extract_all'",
        ),
        ("unsupported_protocol_dl.toml", "URL must start with 'http:' or 'https:'"),
        ("unsupported_protocol_zip.toml", "URL must start with 'http:' or 'https:'"),
        (
            "extract_items_missing_zip_paths.toml",
            "zip_paths is mandatory when action='extract_items'",
        ),
        (
            "extract_items_missing_target_paths.toml",
            "target_paths is mandatory when action='extract_items'",
        ),
        (
            "extract_items_length_not_matching.toml",
            "zip_paths and target_paths must have same length .*",
        ),
        ("unsupported_action.toml", "Unsupported action 'unkwown'"),
    ],
)
def test_errors(config_file: str, exception_message: str):
    """Tests cases with improper configurations"""
    with pytest.raises(Exception, match=exception_message):
        files_install.process(
            str((Path(__file__).parent / "configs" / config_file).absolute())
        )


def test_full(nominal_files: List[str]):
    """Nominal test cases where many files are installed"""

    # Proceed with installation in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Run the file installation
        files_install.process(
            str((Path(__file__).parent / "configs" / "full.toml").absolute())
        )

        # Compare final directory content
        existing_files = [
            str(file.relative_to(temp_dir)) for file in Path(temp_dir).rglob("*.*")
        ]
        # compare set and len, since order does not matter
        assert set(existing_files) == set(nominal_files)
        assert len(existing_files) == len(nominal_files)


def test_assets_already_there_extract_all(nominal_files: List[str]):
    """Assets have already been installed for extract_all action"""

    # Proceed with installation in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create a file which is supposed to be replaced by extract_all
        Path(temp_dir, "part1/action1").mkdir(parents=True, exist_ok=True)
        Path(temp_dir, "part1/action1/something.txt").touch()

        # Run the file installation
        files_install.process(
            str((Path(__file__).parent / "configs" / "full.toml").absolute())
        )

        # Compare final directory content
        existing_files = [
            str(file.relative_to(temp_dir)) for file in Path(temp_dir).rglob("*.*")
        ]
        expected_files = [
            file for file in nominal_files if not file.startswith("part1/action1")
        ] + ["part1/action1/something.txt"]
        # compare set and len, since order does not matter
        assert set(existing_files) == set(expected_files)
        assert len(existing_files) == len(expected_files)


def test_assets_already_there_extract_items(nominal_files: List[str]):
    """Assets have already been installed for extract_items action"""

    # Proceed with installation in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create a file which is supposed to be replaced by extract_items
        Path(temp_dir, "part2/action2").mkdir(parents=True, exist_ok=True)
        Path(temp_dir, "part2/action2/something.txt").touch()

        # Run the file installation
        files_install.process(
            str((Path(__file__).parent / "configs" / "full.toml").absolute())
        )

        # Compare final directory content
        existing_files = [
            str(file.relative_to(temp_dir)) for file in Path(temp_dir).rglob("*.*")
        ]
        expected_files = [
            file for file in nominal_files if not file.startswith("part2/action2")
        ] + ["part2/action2/something.txt"]
        # compare set and len, since order does not matter
        assert set(existing_files) == set(expected_files)
        assert len(existing_files) == len(expected_files)


def test_assets_already_there_get_file(nominal_files: List[str]):
    """Assets have already been installed for get_file action"""

    # Proceed with installation in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create a file which is supposed to be replaced by get_file
        Path(temp_dir, "part4").mkdir(parents=True, exist_ok=True)
        Path(temp_dir, "part4/file4.txt").touch()

        # Run the file installation
        files_install.process(
            str((Path(__file__).parent / "configs" / "full.toml").absolute())
        )

        # Compare final directory content
        existing_files = [
            str(file.relative_to(temp_dir)) for file in Path(temp_dir).rglob("*.*")
        ]
        # compare set and len, since order does not matter
        assert set(existing_files) == set(nominal_files)
        assert len(existing_files) == len(nominal_files)
        assert Path(temp_dir, "part4/file4.txt").lstat().st_size == 0


def test_execute_after_failure():
    """Test case where the execute after command is failing"""

    # Proceed with installation in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        with pytest.raises(
            subprocess.CalledProcessError,
        ):
            files_install.process(
                str(
                    (
                        Path(__file__).parent / "configs/execute_after_failure.toml"
                    ).absolute()
                )
            )
