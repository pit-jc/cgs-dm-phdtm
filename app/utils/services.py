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
            "pdf": "application/pdf",
            "folder": "application/vnd.google-apps.folder",
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

    def list_files(self, folder_id=None, page_size=100, mime_type="folder"):
        """List files in Google Drive or specific folder."""
        try:
            query = f"'{folder_id}' in parents and trashed=false" if folder_id else None

            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    fields="files(id, name, mimeType, createdTime)",
                )
                .execute()
            )

            files = results.get("files", [])
            return files
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
