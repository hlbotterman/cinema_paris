"""Load the cinema configuration from a YAML file."""

import os
from typing import Dict

import yaml


def load_cinemas() -> Dict[str, Dict[str, object]]:
    """Load a list of cinemas from a YAML configuration file.

    It uses the PyYAML library to parse the YAML file and
    returns the data under the key 'cinemas'.

    Returns
    -------
    Dict[str, Dict[str, object]]
        A dictionary where keys are cinema IDs and values are
        dictionaries containing information about each cinema.

    Raises
    ------
    FileNotFoundError: if the 'cinemas.yml' file is not found.

    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "cinemas.yml")

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"The file 'cinemas.yml' was not found at {file_path}"
        )

    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return data["cinemas"]


CINEMAS = load_cinemas()
