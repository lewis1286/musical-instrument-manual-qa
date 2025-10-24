"""
Module Inventory Manager
Manages ChromaDB collection for module capabilities (separate from manual chunks)
"""
import os
import logging
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.services.pdf_processor.module_detector import ModuleInventoryItem, ModuleDetector

# Configure logger
logger = logging.getLogger(__name__)


class ModuleInventoryManager:
    """Manages module capabilities in a separate ChromaDB collection"""

    def __init__(self, db_path: str = "./chroma_db", use_openai: bool = True):
        self.db_path = db_path
        self.use_openai = use_openai

        # Initialize ChromaDB client (shared with main database)
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

        # Get or create collection for module capabilities
        self.collection = self.client.get_or_create_collection(
            name="module_capabilities",
            embedding_function=self.embedding_function,
            metadata={"description": "Module capabilities extracted from manuals"}
        )

        self.module_detector = ModuleDetector()

    def add_module_inventory(self, inventory_item: ModuleInventoryItem) -> None:
        """Add a module inventory item to the database"""
        if not inventory_item.capabilities:
            logger.warning(f"No capabilities detected for {inventory_item.display_name}")
            return

        # Create embedding text optimized for semantic search
        embedding_text = self.module_detector.create_module_embedding_text(inventory_item)

        # Create document ID
        doc_id = f"{inventory_item.manual_filename}_modules"

        # Prepare metadata
        metadata = {
            "filename": inventory_item.manual_filename,
            "display_name": inventory_item.display_name,
            "manufacturer": inventory_item.manufacturer,
            "model": inventory_item.model,
            "instrument_type": inventory_item.instrument_type,
            "total_pages": inventory_item.total_pages,
            "num_capabilities": len(inventory_item.capabilities),
            # Store top capabilities as comma-separated string
            "top_capabilities": ",".join([
                cap.module_type for cap in inventory_item.capabilities[:5]
            ])
        }

        # Add to collection
        self.collection.upsert(
            documents=[embedding_text],
            metadatas=[metadata],
            ids=[doc_id]
        )

        logger.info(f"Added module inventory for {inventory_item.display_name} with {len(inventory_item.capabilities)} capabilities")

    def search_modules_by_capability(
        self, capability_query: str, n_results: int = 5
    ) -> List[Dict]:
        """Search for modules by capability description"""
        logger.info(f"Searching modules by capability: {capability_query}")

        results = self.collection.query(
            query_texts=[capability_query],
            n_results=n_results
        )

        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, document in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if results["distances"] else None

                formatted_results.append({
                    "manual": metadata.get("display_name"),
                    "manufacturer": metadata.get("manufacturer"),
                    "model": metadata.get("model"),
                    "capabilities": metadata.get("top_capabilities", "").split(","),
                    "filename": metadata.get("filename"),
                    "distance": distance,
                    "capability_text": document
                })

        logger.info(f"Found {len(formatted_results)} modules matching query")
        return formatted_results

    def search_by_module_types(
        self, module_types: List[str], require_all: bool = False
    ) -> List[Dict]:
        """Search for manuals that have specific module types"""
        # Create a query from module types
        from app.services.synthesis_knowledge import SynthesisKnowledgeBase
        kb = SynthesisKnowledgeBase()

        query_parts = []
        for module_type in module_types:
            module_info = kb.get_module_type_info(module_type)
            if module_info:
                full_name = module_info.get("full_name", module_type)
                description = module_info.get("description", "")
                query_parts.append(f"{full_name} {description}")

        query = " ".join(query_parts)

        results = self.search_modules_by_capability(query, n_results=10)

        if require_all:
            # Filter to only include modules that have all requested types
            filtered_results = []
            for result in results:
                caps = result.get("capabilities", [])
                if all(mt in caps for mt in module_types):
                    filtered_results.append(result)
            return filtered_results

        return results

    def get_module_inventory_for_manual(self, filename: str) -> Optional[Dict]:
        """Get the module inventory for a specific manual"""
        try:
            results = self.collection.get(
                ids=[f"{filename}_modules"]
            )

            if results["ids"]:
                return {
                    "filename": filename,
                    "metadata": results["metadatas"][0],
                    "capability_text": results["documents"][0]
                }
        except Exception as e:
            logger.error(f"Error retrieving module inventory for {filename}: {e}")

        return None

    def get_all_module_inventories(self) -> List[Dict]:
        """Get all module inventories"""
        try:
            results = self.collection.get()

            inventories = []
            if results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    inventories.append({
                        "id": doc_id,
                        "metadata": results["metadatas"][i],
                        "capability_text": results["documents"][i]
                    })

            return inventories
        except Exception as e:
            logger.error(f"Error retrieving all module inventories: {e}")
            return []

    def delete_module_inventory(self, filename: str) -> bool:
        """Delete module inventory for a specific manual"""
        try:
            self.collection.delete(ids=[f"{filename}_modules"])
            logger.info(f"Deleted module inventory for {filename}")
            return True
        except Exception as e:
            logger.error(f"Error deleting module inventory for {filename}: {e}")
            return False

    def get_capability_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected capabilities across all manuals"""
        inventories = self.get_all_module_inventories()

        # Count capability occurrences
        capability_counts: Dict[str, int] = {}
        total_manuals = len(inventories)

        for inventory in inventories:
            caps = inventory["metadata"].get("top_capabilities", "").split(",")
            for cap in caps:
                if cap:
                    capability_counts[cap] = capability_counts.get(cap, 0) + 1

        return {
            "total_manuals_with_modules": total_manuals,
            "capability_counts": capability_counts,
            "most_common_capabilities": sorted(
                capability_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
        }

    def reset_module_inventory(self) -> bool:
        """Reset the entire module inventory database"""
        try:
            self.client.delete_collection(name="module_capabilities")

            # Recreate the collection
            self.collection = self.client.get_or_create_collection(
                name="module_capabilities",
                embedding_function=self.embedding_function,
                metadata={"description": "Module capabilities extracted from manuals"}
            )

            logger.info("Module inventory database reset successfully")
            return True
        except Exception as e:
            logger.error(f"Error resetting module inventory: {e}")
            return False
