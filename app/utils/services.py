import re, unicodedata
from googleapiclient.discovery import build
from google.auth.credentials import Credentials
from google.oauth2 import service_account

# from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io


class GoogleDriveService:
    def __init__(self, credentials_path):
        """Initialize Google Drive service with service account credentials."""
        self.SCOPES = ["https://www.googleapis.com/auth/drive"]
        # self.SCOPES = ["'https://www.googleapis.com/auth/drive.metadata.readonly'"]
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()
        self.mime_type_map = {
            "pdf": "mimeType='application/pdf'",
            "folder": "mimeType='application/vnd.google-apps.folder'",
        }

    def _authenticate(self):
        """Authenticate using service account credentials."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES
            )
            self.service = build("drive", "v3", credentials=credentials)
            print("Successfully authenticated with Google Drive")
        except Exception as e:
            print(f"Authentication failed: {e}")
            raise e

    def list_files(self, folder_id=None, page_size=100, type="folder"):
        """List files in Google Drive or specific folder."""
        try:
            query = (
                f"'{folder_id}' in parents and trashed=false and {self.mime_type_map[type]}"
                if folder_id
                else None
            )

            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    fields="files(id, name, mimeType, webViewLink, webContentLink, thumbnailLink, fileExtension, createdTime)",
                )
                .execute()
            )

            files = results.get("files", [])
            # Filter out files that start with double underscores
            filtered_files = [
                file for file in files if not file.get("name", "").startswith("__")
            ]

            # return files
            return filtered_files
        except Exception as e:
            print(f"Error listing files: {e}")
            raise e

    def search_files(self, query):
        """Search for files by name or other criteria."""
        try:
            results = (
                self.service.files()
                .list(
                    q=f"name contains '{query}'",
                    fields="files(id, name, mimeType, createdTime)",
                )
                .execute()
            )

            files = results.get("files", [])
            return files
        except Exception as e:
            print(f"Error searching files: {e}")
            raise e

    def get_file_metadata(self, file_id):
        """Get metadata for a specific file."""
        try:
            file = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, mimeType, size, createdTime, modifiedTime, parents",
                )
                .execute()
            )

            return file
        except Exception as e:
            print(f"Error getting file metadata: {e}")
            raise e


def natural_sort_key(text):
    """
    Convert a string into a list of mixed strings and integers for natural sorting.
    This allows proper sorting of strings with numbers (e.g., Area 1, Area 2, ..., Area 10).
    """

    def convert(text_part):
        return int(text_part) if text_part.isdigit() else text_part.lower()

    return [convert(c) for c in re.split(r"(\d+)", text)]


def sort_by_name(items, reverse=False):
    """
    Sort a list of dictionaries by the 'name' key.

    Args:
        items (list): List of dictionaries containing 'name' key
        reverse (bool): If True, sort in descending order

    Returns:
        list: Sorted list of dictionaries by 'name' key
    """
    if not items:
        return []

    return sorted(
        items,
        key=lambda item: (
            natural_sort_key(item.get("name", "")) if isinstance(item, dict) else ""
        ),
        reverse=reverse,
    )


def slugify(text):
    """
    Convert a string to a URL-friendly slug.

    Args:
        text (str): The input string to slugify

    Returns:
        str: A slugified version of the input string
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Normalize unicode characters (remove accents, etc.)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Replace spaces and special characters with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)

    # Remove leading/trailing hyphens and multiple consecutive hyphens
    text = re.sub(r"^-+|-+$", "", text)
    text = re.sub(r"-+", "-", text)

    return text


def unslugify(slug):
    """
    Convert a URL-friendly slug back to a readable string.

    Args:
        slug (str): The slug string to unslugify

    Returns:
        str: A readable version of the slug with spaces and proper capitalization
    """
    if not slug:
        return ""

    # Replace hyphens with spaces
    text = slug.replace("-", " ")

    # Capitalize each word (title case)
    text = text.title()

    return text


def extract_area_and_title(slug):
    """
    Extract area and title from a slug format string containing "area" followed by a number and title.

    Args:
        slug (str): Input slug string (e.g., "area-10-vision-mission-&-goals")

    Returns:
        tuple: A tuple containing (area, title) where:
               - area: "Area X" format (e.g., "Area 10")
               - title: The text after the number with proper formatting (e.g., "Vision Mission & Goals")
               Returns (None, None) if no valid area pattern is found

    Example:
        >>> extract_area_and_title("area-10-vision-mission-&-goals")
        ('Area 10', 'Vision Mission & Goals')
        >>> extract_area_and_title("area-5-research-methods")
        ('Area 5', 'Research Methods')
    """
    if not slug or not isinstance(slug, str):
        return (None, None)

    # Pattern to match "area-number-" at the beginning and capture the rest
    pattern = r"^area-(\d+)-(.+)$"

    match = re.search(pattern, slug.lower())
    if not match:
        return (None, None)

    area_number = match.group(1)
    title_slug = match.group(2)

    # Format area as "Area X"
    area = f"Area {area_number}"

    # Convert slug to readable title
    # Replace hyphens with spaces
    title = title_slug.replace("-", " ")

    # Remove special characters except &
    title = re.sub(r"[^\w\s&]", "", title)

    # Normalize whitespace
    title = re.sub(r"\s+", " ", title).strip()

    # Convert to title case
    title = title.title() if title else ""

    return (area, title)


def contains_pdf_or_folder(text):
    """
    Determine the file type based on text content analysis.

    Analyzes the input text to determine if it represents a PDF file or folder
    by checking for the presence of specific keywords. The function performs
    case-insensitive matching to identify file types based on content indicators.

    Args:
        text (str): The text string to analyze for file type indicators.
                   Should contain the name or description of a file/folder.
                   Expected to be a non-empty string for meaningful analysis.

    Returns:
        str or None: Returns "pdf" if the text contains "pdf" (case-insensitive),
                    "folder" if the text contains "folder" (case-insensitive),
                    or None if the input is not a string or no matching keywords
                    are found.

    Example:
        >>> contains_pdf_or_folder("document.pdf")
        'pdf'
        >>> contains_pdf_or_folder("My Folder")
        'folder'
        >>> contains_pdf_or_folder("image.jpg")
        None
    """
    if not isinstance(text, str):
        return None

    lower_text = text.lower()
    file_type = None
    if "pdf" in lower_text:
        file_type = "pdf"
    elif "folder" in lower_text:
        file_type = "folder"
    return file_type


def format_files_list(files_list):
    """
    Transform a list of files from Google Drive API response to a simplified format.

    Args:
        files_list (list): List of file dictionaries from Google Drive API

    Returns:
        list: List of dictionaries with format {"id": file_id, "name": file_name, "type": file_mimeType}
    """
    if not files_list:
        return []

    formatted_files = []
    for file in files_list:
        formatted_file = {
            "id": file.get("id", ""),
            "name": file.get("name", ""),
            "type": contains_pdf_or_folder(file.get("mimeType", "")),
        }
        formatted_files.append(formatted_file)

    return formatted_files


# # Usage example
# def main():
#     try:
#         # Initialize the service with your credentials file
#         drive_service = GoogleDriveService("./path/to/your/credentials.json")

#         # List files
#         files = drive_service.list_files()
#         print(f"Found {len(files)} files:")
#         for file in files:
#             print(f"- {file['name']} ({file['id']})")

#         # Search for files
#         # search_results = drive_service.search_files('important')

#     except Exception as e:
#         print(f"Error: {e}")
