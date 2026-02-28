"""Seed Azurite blob storage with sample page images."""

import os
import sys
from pathlib import Path

from azure.storage.blob import BlobServiceClient, ContentSettings

CONN_STR = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER", "strategy-pages")
SEED_DIR = Path(__file__).parent


def main() -> None:
    client = BlobServiceClient.from_connection_string(CONN_STR)

    # Create container (ignore if exists)
    try:
        client.create_container(CONTAINER)
        print(f"Created container '{CONTAINER}'")
    except Exception:
        print(f"Container '{CONTAINER}' already exists")

    container = client.get_container_client(CONTAINER)
    count = 0

    for doc_dir in sorted(SEED_DIR.iterdir()):
        if not doc_dir.is_dir():
            continue
        doc_id = doc_dir.name
        for png in sorted(doc_dir.glob("*.png")):
            blob_name = f"{doc_id}/{png.name}"
            print(f"  Uploading {blob_name}...")
            with open(png, "rb") as f:
                container.upload_blob(
                    blob_name,
                    f,
                    overwrite=True,
                    content_settings=ContentSettings(content_type="image/png"),
                )
            count += 1

    print(f"Azurite seeded successfully. {count} page images uploaded.")


if __name__ == "__main__":
    main()
