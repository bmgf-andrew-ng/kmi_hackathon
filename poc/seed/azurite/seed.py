"""Seed Azurite blob storage with sample page images."""

import os
from pathlib import Path

from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

# Azurite well-known dev credentials (same constants as in the MCP server)
_AZURITE_ACCOUNT_NAME = "devstoreaccount1"
_AZURITE_ACCOUNT_KEY = (
    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
    "K1SZFPTOtr/KBHBeksoGMGw=="
)
BLOB_ENDPOINT = os.environ.get(
    "AZURE_STORAGE_BLOB_ENDPOINT", "http://127.0.0.1:10000/devstoreaccount1"
)
CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER", "strategy-pages")
SEED_DIR = Path(__file__).parent


def main() -> None:
    client = BlobServiceClient(
        account_url=BLOB_ENDPOINT,
        credential=AzureNamedKeyCredential(
            name=_AZURITE_ACCOUNT_NAME,
            key=_AZURITE_ACCOUNT_KEY,
        ),
    )

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
