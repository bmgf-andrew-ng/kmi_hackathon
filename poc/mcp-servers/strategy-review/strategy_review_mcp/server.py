"""Strategy Review MCP Server.

Exposes three tools via FastMCP (stdio transport):
  - search_documents: BM25 document-level search on OpenSearch
  - search_chunks: Granular chunk-level search with optional doc_id filter
  - get_page_image: Retrieve a page image from Azurite blob storage (base64)
"""

from __future__ import annotations

import base64
import logging
import os
from typing import Any

from azure.storage.blob import BlobServiceClient
from mcp.server.fastmcp import FastMCP
from opensearchpy import OpenSearch

# ---------------------------------------------------------------------------
# Configuration — read from environment with sensible defaults
# ---------------------------------------------------------------------------

OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL", "http://localhost:9200")
OPENSEARCH_USER = os.environ.get("OPENSEARCH_USER", "admin")
OPENSEARCH_PASSWORD = os.environ.get("OPENSEARCH_PASSWORD", "admin")
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "strategy-chunks")

AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
    "K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1",
)
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER", "strategy-pages")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "Strategy Review",
    instructions=(
        "Search strategy documents and retrieve page images. "
        "Backed by OpenSearch (BM25) and Azure Blob Storage (Azurite)."
    ),
)

# ---------------------------------------------------------------------------
# Lazy client singletons (created on first use, not at import time)
# ---------------------------------------------------------------------------

_opensearch_client: OpenSearch | None = None
_blob_service_client: BlobServiceClient | None = None


def _get_opensearch_client() -> OpenSearch:
    """Return a singleton OpenSearch client, creating it on first call."""
    global _opensearch_client
    if _opensearch_client is None:
        _opensearch_client = OpenSearch(
            hosts=[OPENSEARCH_URL],
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD)
            if OPENSEARCH_USER
            else None,
            use_ssl=OPENSEARCH_URL.startswith("https"),
            verify_certs=False,
            timeout=30,
        )
    return _opensearch_client


def _get_blob_service_client() -> BlobServiceClient:
    """Return a singleton BlobServiceClient, creating it on first call."""
    global _blob_service_client
    if _blob_service_client is None:
        _blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )
    return _blob_service_client


# ---------------------------------------------------------------------------
# Tool: search_documents
# ---------------------------------------------------------------------------


@mcp.tool()
def search_documents(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search strategy documents by keyword query.

    Performs a BM25 multi_match search across document titles and chunk text,
    then aggregates results at the document level. Returns the top-scoring
    documents with their best matching chunk as a preview snippet.

    Args:
        query: The search query string (e.g. "maternal health", "TB elimination").
        top_k: Maximum number of documents to return. Defaults to 5.

    Returns:
        A list of document results, each containing doc_id, doc_title,
        doc_year, organization, score, snippet, section, page_number,
        and themes.
    """
    try:
        client = _get_opensearch_client()

        body: dict[str, Any] = {
            "size": top_k * 5,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["doc_title^2", "chunk_text"],
                    "type": "best_fields",
                }
            },
            "_source": [
                "doc_id",
                "doc_title",
                "doc_year",
                "organization",
                "chunk_text",
                "section",
                "page_number",
                "themes",
            ],
        }

        response = client.search(index=OPENSEARCH_INDEX, body=body)
        hits = response.get("hits", {}).get("hits", [])

        # Aggregate: keep only the top-scoring chunk per doc_id
        docs: dict[str, dict[str, Any]] = {}
        for hit in hits:
            src = hit["_source"]
            did = src["doc_id"]
            score = hit["_score"]
            if did not in docs or score > docs[did]["score"]:
                docs[did] = {
                    "doc_id": did,
                    "doc_title": src.get("doc_title", ""),
                    "doc_year": src.get("doc_year"),
                    "organization": src.get("organization", ""),
                    "score": score,
                    "snippet": src.get("chunk_text", "")[:500],
                    "section": src.get("section", ""),
                    "page_number": src.get("page_number"),
                    "themes": src.get("themes", []),
                }

        results = sorted(docs.values(), key=lambda d: d["score"], reverse=True)
        return results[:top_k]

    except Exception as e:
        logger.exception("search_documents failed")
        return [{"error": f"Search failed: {e}"}]


# ---------------------------------------------------------------------------
# Tool: search_chunks
# ---------------------------------------------------------------------------


@mcp.tool()
def search_chunks(
    query: str, doc_id: str | None = None, top_k: int = 5
) -> list[dict[str, Any]]:
    """Search within strategy document chunks at a granular level.

    Performs a BM25 match on chunk_text with an optional doc_id filter
    to restrict results to a specific document.

    Args:
        query: The search query string.
        doc_id: Optional document ID to filter chunks (e.g. "GH_2024").
            If None, searches across all documents.
        top_k: Maximum number of chunks to return. Defaults to 5.

    Returns:
        A list of chunk results, each containing chunk_id, doc_id,
        doc_title, score, chunk_text, section, page_number, themes,
        countries, and chunk_order.
    """
    try:
        client = _get_opensearch_client()

        must_clauses: list[dict[str, Any]] = [{"match": {"chunk_text": query}}]
        filter_clauses: list[dict[str, Any]] = []

        if doc_id is not None:
            filter_clauses.append({"term": {"doc_id": doc_id}})

        body: dict[str, Any] = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses,
                }
            },
            "_source": [
                "chunk_id",
                "doc_id",
                "doc_title",
                "chunk_text",
                "section",
                "page_number",
                "themes",
                "countries",
                "chunk_order",
            ],
        }

        response = client.search(index=OPENSEARCH_INDEX, body=body)
        hits = response.get("hits", {}).get("hits", [])

        return [
            {
                "chunk_id": hit["_source"].get("chunk_id", ""),
                "doc_id": hit["_source"].get("doc_id", ""),
                "doc_title": hit["_source"].get("doc_title", ""),
                "score": hit["_score"],
                "chunk_text": hit["_source"].get("chunk_text", ""),
                "section": hit["_source"].get("section", ""),
                "page_number": hit["_source"].get("page_number"),
                "themes": hit["_source"].get("themes", []),
                "countries": hit["_source"].get("countries", []),
                "chunk_order": hit["_source"].get("chunk_order"),
            }
            for hit in hits
        ]

    except Exception as e:
        logger.exception("search_chunks failed")
        return [{"error": f"Chunk search failed: {e}"}]


# ---------------------------------------------------------------------------
# Tool: get_page_image
# ---------------------------------------------------------------------------


@mcp.tool()
def get_page_image(doc_id: str, page_num: int) -> dict[str, Any]:
    """Retrieve a page image from Azure Blob Storage (Azurite).

    Fetches the PNG image for a specific page of a strategy document.
    The blob naming convention is: {doc_id}/page_{page_num:03d}.png

    Args:
        doc_id: Document identifier (e.g. "GH_2024").
        page_num: Page number to retrieve (1-indexed).

    Returns:
        A dict containing doc_id, page_num, image_base64, and content_type.
        Returns an error dict if the blob is not found.
    """
    blob_name = f"{doc_id}/page_{page_num:03d}.png"
    try:
        blob_service = _get_blob_service_client()
        container_client = blob_service.get_container_client(
            AZURE_STORAGE_CONTAINER
        )
        blob_client = container_client.get_blob_client(blob_name)

        download = blob_client.download_blob()
        image_bytes = download.readall()
        content_type = (
            download.properties.content_settings.content_type or "image/png"
        )

        return {
            "doc_id": doc_id,
            "page_num": page_num,
            "image_base64": base64.b64encode(image_bytes).decode("utf-8"),
            "content_type": content_type,
        }

    except Exception as e:
        error_str = str(e)
        error_name = type(e).__name__

        if "ResourceNotFoundError" in error_name or "BlobNotFound" in error_str:
            return {
                "error": (
                    f"Page image not found: blob '{blob_name}' does not exist "
                    f"in container '{AZURE_STORAGE_CONTAINER}'. "
                    f"Page images may not have been seeded yet."
                ),
                "doc_id": doc_id,
                "page_num": page_num,
            }

        if "ContainerNotFound" in error_str:
            return {
                "error": (
                    f"Container '{AZURE_STORAGE_CONTAINER}' does not exist. "
                    f"Azurite blob storage may not have been seeded."
                ),
                "doc_id": doc_id,
                "page_num": page_num,
            }

        logger.exception("get_page_image failed")
        return {
            "error": f"Failed to retrieve page image: {e}",
            "doc_id": doc_id,
            "page_num": page_num,
        }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the Strategy Review MCP server (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
