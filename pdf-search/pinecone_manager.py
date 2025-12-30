"""
Pinecone Manager for vector operations.
Handles index creation, upsert, search, and deletion.
"""

import time
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from config import Config


class PineconeManager:
    """Manages all Pinecone vector database operations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        namespace: Optional[str] = None
    ):
        """
        Initialize Pinecone manager.

        Args:
            api_key: Pinecone API key (defaults to Config.PINECONE_API_KEY)
            index_name: Index name (defaults to Config.PINECONE_INDEX_NAME)
            namespace: Namespace (defaults to Config.PINECONE_NAMESPACE)
        """
        self.api_key = api_key or Config.PINECONE_API_KEY
        self.index_name = index_name or Config.PINECONE_INDEX_NAME
        self.namespace = namespace or Config.PINECONE_NAMESPACE

        if not self.api_key:
            raise ValueError("Pinecone API key is required")

        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None

    def create_index(
        self,
        dimension: int = Config.EMBEDDING_DIMENSION,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = Config.PINECONE_ENVIRONMENT
    ) -> None:
        """
        Create a new Pinecone index with serverless embedding.

        Args:
            dimension: Embedding dimension
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider (aws, gcp, azure)
            region: Cloud region
        """
        if self.index_name in self.pc.list_indexes().names():
            print(f"Index '{self.index_name}' already exists")
            return

        print(f"Creating index '{self.index_name}' with dimension {dimension}...")

        self.pc.create_index(
            name=self.index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=cloud,
                region=region
            )
        )

        # Wait for index to be ready
        while not self.pc.describe_index(self.index_name).status['ready']:
            print("Waiting for index to be ready...")
            time.sleep(1)

        print(f"✓ Index '{self.index_name}' created successfully")

    def get_index(self):
        """Get or connect to the index."""
        if self.index is None:
            if self.index_name not in self.pc.list_indexes().names():
                raise ValueError(
                    f"Index '{self.index_name}' does not exist. "
                    "Create it first using create_index()"
                )
            self.index = self.pc.Index(self.index_name)

        return self.index

    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> Dict[str, int]:
        """
        Upsert document chunks to Pinecone.

        Args:
            chunks: List of chunk dicts with 'id', 'text', and 'metadata'
            batch_size: Number of chunks to upsert per batch
            show_progress: Show progress bar

        Returns:
            Dict with upsert statistics

        Expected chunk format:
        {
            'id': 'doc_id#chunk_1',
            'text': 'chunk text content',
            'metadata': {
                'document_id': 'doc_id',
                'document_title': 'Title',
                'chunk_number': 1,
                'chunk_text': 'chunk text',
                ...
            }
        }
        """
        index = self.get_index()

        # Prepare vectors for upsert
        # Note: With Pinecone's serverless embedding, we send text directly
        # The embedding happens server-side
        vectors = []
        for chunk in chunks:
            vectors.append({
                'id': chunk['id'],
                'values': chunk.get('values', []),  # Empty if using server-side embedding
                'metadata': chunk['metadata']
            })

        # Upsert in batches
        total_upserted = 0
        failed = 0

        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(
                    range(0, len(vectors), batch_size),
                    desc="Upserting chunks"
                )
            except ImportError:
                iterator = range(0, len(vectors), batch_size)
                print(f"Upserting {len(vectors)} chunks in batches of {batch_size}...")
        else:
            iterator = range(0, len(vectors), batch_size)

        for i in iterator:
            batch = vectors[i:i + batch_size]
            try:
                index.upsert(
                    vectors=batch,
                    namespace=self.namespace
                )
                total_upserted += len(batch)
            except Exception as e:
                print(f"Error upserting batch {i//batch_size}: {e}")
                failed += len(batch)

        # Wait for eventual consistency
        time.sleep(1)

        return {
            'total': len(chunks),
            'upserted': total_upserted,
            'failed': failed
        }

    def search(
        self,
        query: str,
        top_k: int = Config.DEFAULT_TOP_K,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_values: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across indexed chunks.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Metadata filters (e.g., {'document_id': 'doc_001'})
            include_metadata: Include metadata in results
            include_values: Include vector values in results

        Returns:
            List of search results with scores and metadata
        """
        index = self.get_index()

        # Note: With serverless embedding, query text is sent directly
        # Pinecone handles embedding server-side
        results = index.query(
            vector=query if isinstance(query, list) else None,  # If pre-embedded
            data=query if isinstance(query, str) else None,  # If text query
            top_k=top_k,
            filter=filter_metadata,
            include_metadata=include_metadata,
            include_values=include_values,
            namespace=self.namespace
        )

        # Format results
        formatted_results = []
        for match in results.get('matches', []):
            result = {
                'id': match['id'],
                'score': match['score'],
            }
            if include_metadata and 'metadata' in match:
                result['metadata'] = match['metadata']
            if include_values and 'values' in match:
                result['values'] = match['values']

            formatted_results.append(result)

        return formatted_results

    def delete_by_document_id(
        self,
        document_id: str
    ) -> Dict[str, Any]:
        """
        Delete all chunks for a specific document.

        Args:
            document_id: Document identifier

        Returns:
            Deletion statistics
        """
        index = self.get_index()

        try:
            # Delete by metadata filter
            index.delete(
                filter={'document_id': document_id},
                namespace=self.namespace
            )

            # Wait for deletion to complete
            time.sleep(1)

            return {
                'success': True,
                'document_id': document_id,
                'message': f"Deleted all chunks for document '{document_id}'"
            }
        except Exception as e:
            return {
                'success': False,
                'document_id': document_id,
                'error': str(e)
            }

    def delete_by_ids(
        self,
        chunk_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete specific chunks by their IDs.

        Args:
            chunk_ids: List of chunk IDs to delete

        Returns:
            Deletion statistics
        """
        index = self.get_index()

        try:
            index.delete(
                ids=chunk_ids,
                namespace=self.namespace
            )

            time.sleep(1)

            return {
                'success': True,
                'deleted_count': len(chunk_ids),
                'message': f"Deleted {len(chunk_ids)} chunks"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_by_prefix(
        self,
        prefix: str,
        limit: int = 100
    ) -> List[str]:
        """
        List chunk IDs with a given prefix.

        Args:
            prefix: ID prefix (e.g., 'doc_001#' for all chunks of doc_001)
            limit: Maximum number of IDs to return

        Returns:
            List of matching chunk IDs
        """
        index = self.get_index()

        # Note: This uses a query with metadata filter
        # Adjust based on your ID structure
        try:
            results = index.query(
                vector=[0] * Config.EMBEDDING_DIMENSION,  # Dummy vector
                top_k=limit,
                filter={'document_id': prefix.rstrip('#')},
                include_metadata=False,
                namespace=self.namespace
            )

            return [match['id'] for match in results.get('matches', [])]
        except Exception as e:
            print(f"Error listing by prefix: {e}")
            return []

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Index statistics including vector count, dimension, etc.
        """
        index = self.get_index()

        stats = index.describe_index_stats()

        return {
            'total_vector_count': stats.get('total_vector_count', 0),
            'dimension': stats.get('dimension', 0),
            'index_fullness': stats.get('index_fullness', 0),
            'namespaces': stats.get('namespaces', {})
        }

    def delete_index(self, confirm: bool = False) -> None:
        """
        Delete the entire index.

        Args:
            confirm: Must be True to actually delete

        Warning:
            This deletes ALL data in the index. Use with caution!
        """
        if not confirm:
            raise ValueError(
                "Must set confirm=True to delete index. "
                "This action cannot be undone!"
            )

        if self.index_name in self.pc.list_indexes().names():
            self.pc.delete_index(self.index_name)
            print(f"✓ Index '{self.index_name}' deleted")
        else:
            print(f"Index '{self.index_name}' does not exist")


if __name__ == "__main__":
    # Test Pinecone connection
    try:
        manager = PineconeManager()
        print("✓ Pinecone manager initialized")

        # Try to get index stats
        try:
            stats = manager.get_index_stats()
            print(f"✓ Connected to index '{manager.index_name}'")
            print(f"  Total vectors: {stats['total_vector_count']}")
            print(f"  Dimension: {stats['dimension']}")
        except Exception as e:
            print(f"Index not found or not accessible: {e}")
            print("Run scripts/create_index.py to create the index first")

    except Exception as e:
        print(f"✗ Error initializing Pinecone: {e}")
        print("Check your .env file and API key")
