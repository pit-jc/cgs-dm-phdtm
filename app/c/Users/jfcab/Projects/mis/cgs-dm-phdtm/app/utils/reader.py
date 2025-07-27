import yaml
import os
from typing import Dict, Any, Optional


def read_models_yml(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Read and parse the contents of the models.yml file.

    Args:
        file_path (Optional[str]): Path to the models.yml file.
                                 If None, uses the default path in utils directory.

    Returns:
        Dict[str, Any]: Parsed YAML content as a dictionary

    Raises:
        FileNotFoundError: If the models.yml file doesn't exist
        yaml.YAMLError: If there's an error parsing the YAML content
    """
    if file_path is None:
        # Get the directory of this script and construct path to models.yml
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "models.yml")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = yaml.safe_load(file)
            return content if content is not None else {}
    except FileNotFoundError:
        raise FileNotFoundError(f"models.yml file not found at: {file_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML content: {e}")


def get_model_by_name(
    model_name: str, file_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a specific model configuration by name from models.yml.

    Args:
        model_name (str): Name of the model to retrieve
        file_path (Optional[str]): Path to the models.yml file

    Returns:
        Optional[Dict[str, Any]]: Model configuration if found, None otherwise
    """
    models = read_models_yml(file_path)
    return models.get(model_name)


def list_available_models(file_path: Optional[str] = None) -> list:
    """
    Get a list of all available model names from models.yml.

    Args:
        file_path (Optional[str]): Path to the models.yml file

    Returns:
        list: List of model names
    """
    models = read_models_yml(file_path)
    return list(models.keys()) if isinstance(models, dict) else []
