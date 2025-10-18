import os
import json
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

from src.pdf_processor.pdf_extractor import DocumentChunk, ManualMetadata

class ChromaManager:
    """Manages ChromaDB vector database for musical instrument manuals"""

    def __init__(self, db_path: str = "./chroma_db", use_openai: bool = True):
        self.db_path = db_path
        self.use_openai = use_openai

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)

        # Initialize embeddings
        if use_openai and os.getenv("OPENAI_API_KEY"):
            self.embeddings = OpenAIEmbeddings()
            self.embedding_function = chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name="text-embedding-ada-002"
            )
        else:
            # Fallback to local embeddings
            model_name = "all-MiniLM-L6-v2"
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
            self.embedding_function = chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_name
            )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="manual_chunks",
            embedding_function=self.embedding_function,
            metadata={"description": "Musical instrument manual chunks"}
        )

    def add_manual_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Add manual chunks to the vector database"""
        if not chunks:
            return

        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{chunk.metadata.filename}_{chunk.page_number}_{chunk.chunk_index}"
            ids.append(chunk_id)

            # Prepare document content
            documents.append(chunk.content)

            # Prepare metadata
            metadata = {
                "filename": chunk.metadata.filename,
                "display_name": chunk.metadata.display_name or chunk.metadata.filename,
                "manufacturer": chunk.metadata.manufacturer or "unknown",
                "model": chunk.metadata.model or "unknown",
                "instrument_type": chunk.metadata.instrument_type or "unknown",
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "section_type": chunk.section_type or "general",
                "total_pages": chunk.metadata.total_pages
            }
            metadatas.append(metadata)

        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(chunks)} chunks to vector database")

    def search_similar(self, query: str, n_results: int = 5,
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Search for similar chunks based on query"""
        where_clause = {}

        if filters:
            if "instrument_type" in filters and filters["instrument_type"]:
                where_clause["instrument_type"] = filters["instrument_type"]
            if "manufacturer" in filters and filters["manufacturer"]:
                where_clause["manufacturer"] = filters["manufacturer"]
            if "section_type" in filters and filters["section_type"]:
                where_clause["section_type"] = filters["section_type"]

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )

        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, document in enumerate(results["documents"][0]):
                result = {
                    "content": document,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "id": results["ids"][0][i]
                }
                formatted_results.append(result)

        return formatted_results

    def search_by_keywords(self, keywords: List[str], n_results: int = 5,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Search using keyword matching combined with semantic search"""
        # Combine keywords into a query
        query = " ".join(keywords)
        return self.search_similar(query, n_results, filters)

    def get_all_manuals(self) -> List[Dict]:
        """Get list of all uploaded manuals with metadata"""
        # Get all documents and group by filename
        all_results = self.collection.get()

        manuals = {}
        for i, metadata in enumerate(all_results["metadatas"]):
            filename = metadata["filename"]
            if filename not in manuals:
                manuals[filename] = {
                    "filename": filename,
                    "display_name": metadata.get("display_name", filename),
                    "manufacturer": metadata.get("manufacturer", "unknown"),
                    "model": metadata.get("model", "unknown"),
                    "instrument_type": metadata.get("instrument_type", "unknown"),
                    "total_pages": metadata.get("total_pages", 0),
                    "chunk_count": 0
                }
            manuals[filename]["chunk_count"] += 1

        return list(manuals.values())

    def delete_manual(self, filename: str) -> bool:
        """Delete all chunks for a specific manual"""
        try:
            # Get all chunks for this manual
            results = self.collection.get(
                where={"filename": filename}
            )

            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"Deleted {len(results['ids'])} chunks for {filename}")
                return True
            else:
                print(f"No chunks found for {filename}")
                return False

        except Exception as e:
            print(f"Error deleting manual {filename}: {e}")
            return False

    def get_unique_values(self, field: str) -> List[str]:
        """Get unique values for a metadata field"""
        all_results = self.collection.get()
        values = set()

        for metadata in all_results["metadatas"]:
            if field in metadata and metadata[field]:
                values.add(metadata[field])

        return sorted(list(values))

    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        all_results = self.collection.get()

        stats = {
            "total_chunks": len(all_results["ids"]) if all_results["ids"] else 0,
            "total_manuals": len(set(m.get("filename", "") for m in all_results["metadatas"])),
            "manufacturers": self.get_unique_values("manufacturer"),
            "instrument_types": self.get_unique_values("instrument_type"),
            "section_types": self.get_unique_values("section_type")
        }

        return stats

    def hybrid_search(self, query: str, keywords: List[str] = None,
                     n_results: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Perform hybrid search combining semantic similarity and keyword matching"""
        # Start with semantic search
        semantic_results = self.search_similar(query, n_results * 2, filters)

        # If keywords provided, boost results containing keywords
        if keywords:
            keyword_query = " ".join(keywords)
            keyword_results = self.search_similar(keyword_query, n_results, filters)

            # Combine and deduplicate results
            seen_ids = set()
            combined_results = []

            # Add keyword results first (higher priority)
            for result in keyword_results:
                if result["id"] not in seen_ids:
                    combined_results.append(result)
                    seen_ids.add(result["id"])

            # Add semantic results
            for result in semantic_results:
                if result["id"] not in seen_ids and len(combined_results) < n_results:
                    combined_results.append(result)
                    seen_ids.add(result["id"])

            return combined_results[:n_results]

        return semantic_results[:n_results]

    def reset_database(self) -> bool:
        """Reset the entire database - delete all data"""
        try:
            # Delete the collection
            self.client.delete_collection(name="manual_chunks")

            # Recreate the collection
            self.collection = self.client.get_or_create_collection(
                name="manual_chunks",
                embedding_function=self.embedding_function,
                metadata={"description": "Musical instrument manual chunks"}
            )

            print("Database reset successfully")
            return True

        except Exception as e:
            print(f"Error resetting database: {e}")
            return False