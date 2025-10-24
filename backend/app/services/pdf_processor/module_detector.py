"""
Module capability detection from manual text
Analyzes PDF content to identify modular synthesis module types and capabilities
"""
import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

from app.services.synthesis_knowledge import SynthesisKnowledgeBase
from app.services.pdf_processor.pdf_extractor import DocumentChunk, ManualMetadata


@dataclass
class ModuleCapability:
    """Detected module capability from manual"""
    module_type: str
    confidence: float  # 0.0 to 1.0
    detected_features: List[str]
    page_numbers: List[int]
    text_evidence: List[str]  # Snippets that support detection


@dataclass
class ModuleInventoryItem:
    """A module extracted from a manual with its capabilities"""
    manual_filename: str
    display_name: str
    manufacturer: str
    model: str
    capabilities: List[ModuleCapability]
    total_pages: int
    instrument_type: str


class ModuleDetector:
    """Detects module capabilities from manual chunks"""

    def __init__(self):
        self.knowledge_base = SynthesisKnowledgeBase()
        self.all_module_types = self.knowledge_base.get_all_module_types()

    def analyze_manual_for_modules(
        self, chunks: List[DocumentChunk], metadata: ManualMetadata
    ) -> ModuleInventoryItem:
        """Analyze all chunks to detect module capabilities"""
        # Collect evidence for each module type
        module_evidence: Dict[str, Dict] = {
            module_type: {
                "matches": 0,
                "page_numbers": set(),
                "features": set(),
                "text_snippets": []
            }
            for module_type in self.all_module_types
        }

        # Scan all chunks for module type indicators
        for chunk in chunks:
            self._analyze_chunk(chunk, module_evidence)

        # Convert evidence to capabilities with confidence scores
        capabilities = self._compute_capabilities(module_evidence, len(chunks))

        return ModuleInventoryItem(
            manual_filename=metadata.filename,
            display_name=metadata.display_name,
            manufacturer=metadata.manufacturer or "Unknown",
            model=metadata.model or "Unknown",
            capabilities=capabilities,
            total_pages=metadata.total_pages,
            instrument_type=metadata.instrument_type or "modular"
        )

    def _analyze_chunk(self, chunk: DocumentChunk, module_evidence: Dict):
        """Analyze a single chunk for module type indicators"""
        text = chunk.content.lower()

        for module_type in self.all_module_types:
            # Get detection patterns for this module type
            patterns = self.knowledge_base.get_module_detection_patterns(module_type)
            module_info = self.knowledge_base.get_module_type_info(module_type)

            for pattern in patterns:
                # Use regex to find matches
                if re.search(pattern.lower(), text):
                    module_evidence[module_type]["matches"] += 1
                    module_evidence[module_type]["page_numbers"].add(chunk.page_number)

                    # Extract context snippet
                    match = re.search(f".{{0,50}}{pattern.lower()}.{{0,50}}", text)
                    if match:
                        snippet = match.group().strip()
                        if snippet not in module_evidence[module_type]["text_snippets"]:
                            module_evidence[module_type]["text_snippets"].append(snippet)

            # Look for specific features/specifications
            if module_info and "specifications" in module_info:
                for spec in module_info["specifications"]:
                    spec_name = spec.get("name", "")
                    # Check for specification keywords
                    if spec_name in text or any(
                        opt in text for opt in spec.get("options", []) if isinstance(opt, str)
                    ):
                        module_evidence[module_type]["features"].add(spec_name)

    def _compute_capabilities(
        self, module_evidence: Dict, total_chunks: int
    ) -> List[ModuleCapability]:
        """Convert evidence into capability objects with confidence scores"""
        capabilities = []

        for module_type, evidence in module_evidence.items():
            matches = evidence["matches"]

            if matches == 0:
                continue  # No evidence for this module type

            # Compute confidence based on:
            # - Number of pattern matches
            # - Number of pages mentioning it
            # - Number of detected features
            match_score = min(matches / 5.0, 1.0)  # Cap at 5 matches
            page_score = min(len(evidence["page_numbers"]) / 3.0, 1.0)  # Cap at 3 pages
            feature_score = min(len(evidence["features"]) / 3.0, 1.0)  # Cap at 3 features

            # Weighted average
            confidence = (match_score * 0.5 + page_score * 0.3 + feature_score * 0.2)

            # Only include if confidence is above threshold
            if confidence >= 0.2:
                capabilities.append(
                    ModuleCapability(
                        module_type=module_type,
                        confidence=confidence,
                        detected_features=list(evidence["features"]),
                        page_numbers=sorted(list(evidence["page_numbers"])),
                        text_evidence=evidence["text_snippets"][:3]  # Top 3 snippets
                    )
                )

        # Sort by confidence
        capabilities.sort(key=lambda x: x.confidence, reverse=True)

        return capabilities

    def get_module_summary(self, inventory_item: ModuleInventoryItem) -> str:
        """Generate human-readable summary of detected modules"""
        if not inventory_item.capabilities:
            return f"{inventory_item.display_name}: No specific module types detected"

        summary_lines = [f"{inventory_item.display_name} modules:"]
        for cap in inventory_item.capabilities:
            module_info = self.knowledge_base.get_module_type_info(cap.module_type)
            full_name = module_info.get("full_name", cap.module_type.upper())
            confidence_pct = int(cap.confidence * 100)

            features_str = ", ".join(cap.detected_features[:3]) if cap.detected_features else "basic"
            summary_lines.append(
                f"  - {full_name} ({confidence_pct}% confidence) - {features_str}"
            )

        return "\n".join(summary_lines)

    def create_module_embedding_text(self, inventory_item: ModuleInventoryItem) -> str:
        """Create text optimized for semantic search embeddings"""
        # This text will be embedded in ChromaDB for module capability search
        parts = [
            f"Manual: {inventory_item.display_name}",
            f"Manufacturer: {inventory_item.manufacturer}",
            f"Model: {inventory_item.model}",
            "Capabilities:"
        ]

        for cap in inventory_item.capabilities:
            module_info = self.knowledge_base.get_module_type_info(cap.module_type)
            full_name = module_info.get("full_name", cap.module_type)
            description = module_info.get("description", "")

            parts.append(f"{full_name}: {description}")

            if cap.detected_features:
                parts.append(f"  Features: {', '.join(cap.detected_features)}")

            # Add some text evidence for context
            if cap.text_evidence:
                parts.append(f"  Context: {cap.text_evidence[0]}")

        return "\n".join(parts)
