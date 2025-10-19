import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

from app.services.vector_db.chroma_manager import ChromaManager
from app.core.config import settings

@dataclass
class QAResponse:
    """Response from the QA system"""
    answer: str
    sources: List[Dict]
    confidence: Optional[float] = None
    query: str = ""

class MusicalInstrumentQA:
    """RAG-based QA system for musical instrument manuals"""

    def __init__(self, chroma_manager: ChromaManager, model_name: str = settings.anthropic_model):
        self.chroma_manager = chroma_manager
        self.model_name = model_name

        # Initialize language model
        if os.getenv("ANTHROPIC_API_KEY"):
            self.llm = ChatAnthropic(
                model=model_name,
                temperature=0.1,
                max_tokens=1000
            )
        else:
            raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable.")

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # System prompt for musical instrument context
        self.system_prompt = """You are an expert assistant for musical instrument manuals.
You help musicians, producers, and audio engineers understand how to use their equipment.

Guidelines:
- Provide clear, practical answers based on the manual content provided
- Include specific page references when available
- For technical specifications, be precise and accurate
- For setup instructions, provide step-by-step guidance
- If information is not in the provided context, say so clearly
- Use musical terminology appropriately
- Consider both beginner and advanced user needs

Context from manuals:
{context}

Question: {question}

Answer based on the manual content provided:"""

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from user query"""
        # Remove common words and extract meaningful terms
        stop_words = {'how', 'what', 'where', 'when', 'why', 'is', 'are', 'can', 'do', 'does', 'the', 'a', 'an', 'to', 'for', 'with', 'and', 'or'}

        # Split and clean
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Add musical instrument specific terms
        musical_terms = []
        query_lower = query.lower()

        # Common musical terms to boost
        if any(term in query_lower for term in ['midi', 'cv', 'gate']):
            musical_terms.extend(['midi', 'cv', 'gate'])
        if any(term in query_lower for term in ['connect', 'connection', 'input', 'output']):
            musical_terms.extend(['connect', 'connection', 'input', 'output'])
        if any(term in query_lower for term in ['preset', 'patch', 'program']):
            musical_terms.extend(['preset', 'patch', 'program'])

        return keywords + musical_terms

    def _parse_query_filters(self, query: str) -> Dict:
        """Parse query for filtering hints"""
        filters = {}
        query_lower = query.lower()

        # Instrument type detection
        if any(term in query_lower for term in ['synthesizer', 'synth']):
            filters['instrument_type'] = 'synthesizer'
        elif any(term in query_lower for term in ['keyboard', 'piano']):
            filters['instrument_type'] = 'keyboard'
        elif any(term in query_lower for term in ['mixer', 'mixing']):
            filters['instrument_type'] = 'mixer'
        elif any(term in query_lower for term in ['drum', 'rhythm']):
            filters['instrument_type'] = 'drum_machine'

        # Manufacturer detection
        manufacturers = ['moog', 'roland', 'korg', 'yamaha', 'nord', 'arturia', 'novation']
        for manufacturer in manufacturers:
            if manufacturer in query_lower:
                filters['manufacturer'] = manufacturer.title()

        return filters

    def answer_question(self, query: str, max_sources: int = 5,
                       include_conversation: bool = True) -> QAResponse:
        """Answer a question using the RAG pipeline"""

        # Extract keywords and filters
        keywords = self._extract_keywords(query)
        filters = self._parse_query_filters(query)

        # Retrieve relevant chunks
        relevant_chunks = self.chroma_manager.hybrid_search(
            query=query,
            keywords=keywords,
            n_results=max_sources,
            filters=filters
        )

        if not relevant_chunks:
            return QAResponse(
                answer="I couldn't find relevant information in the uploaded manuals. Please make sure you've uploaded the manual for the instrument you're asking about.",
                sources=[],
                query=query
            )

        # Prepare context for the LLM
        context_parts = []
        sources = []

        for i, chunk in enumerate(relevant_chunks):
            metadata = chunk["metadata"]
            display_name = metadata.get("display_name", metadata["filename"])
            source_info = f"[Source {i+1}: {display_name}, Page {metadata['page_number']}]"

            context_parts.append(f"{source_info}\n{chunk['content']}")

            sources.append({
                "filename": metadata["filename"],
                "display_name": display_name,
                "page_number": metadata["page_number"],
                "manufacturer": metadata.get("manufacturer", "unknown"),
                "model": metadata.get("model", "unknown"),
                "instrument_type": metadata.get("instrument_type", "unknown"),
                "section_type": metadata.get("section_type", "general"),
                "content_preview": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"]
            })

        context = "\n\n".join(context_parts)

        # Include conversation history if requested
        conversation_context = ""
        if include_conversation and self.memory.chat_memory.messages:
            conversation_context = "\n\nPrevious conversation:\n"
            for message in self.memory.chat_memory.messages[-4:]:  # Last 2 exchanges
                if hasattr(message, 'content'):
                    conversation_context += f"{message.__class__.__name__}: {message.content}\n"

        # Generate answer using LLM
        full_prompt = self.system_prompt.format(
            context=context + conversation_context,
            question=query
        )

        try:
            messages = [
                SystemMessage(content="You are an expert assistant for musical instrument manuals."),
                HumanMessage(content=full_prompt)
            ]

            response = self.llm(messages)
            answer = response.content

            # Store in conversation memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(answer)

        except Exception as e:
            answer = f"Error generating response: {str(e)}"

        return QAResponse(
            answer=answer,
            sources=sources,
            query=query
        )

    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history"""
        history = []
        messages = self.memory.chat_memory.messages

        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "question": messages[i].content,
                    "answer": messages[i + 1].content
                })

        return history

    def clear_conversation(self):
        """Clear the conversation memory"""
        self.memory.clear()

    def suggest_questions(self, instrument_type: Optional[str] = None) -> List[str]:
        """Suggest common questions based on available manuals"""
        suggestions = [
            "How do I set up MIDI connections?",
            "What are the audio input and output specifications?",
            "How do I save and load presets?",
            "How do I connect to a computer via USB?",
            "What is the power consumption?",
            "How do I perform a factory reset?",
            "How do I update the firmware?",
            "What are the CV/Gate specifications?",
        ]

        # Add instrument-specific suggestions
        if instrument_type == "synthesizer":
            suggestions.extend([
                "How do I program a new patch?",
                "How do the filters work?",
                "How do I set up LFO modulation?",
                "How do I use the arpeggiator?",
                "How do I sync to external clock?"
            ])
        elif instrument_type == "mixer":
            suggestions.extend([
                "How do I set up auxiliary sends?",
                "How do I use the built-in effects?",
                "How do I record the mix?",
                "How do I set up monitor mixes?",
                "How do I use the EQ controls?"
            ])
        elif instrument_type == "drum_machine":
            suggestions.extend([
                "How do I program a drum pattern?",
                "How do I change individual drum sounds?",
                "How do I chain patterns together?",
                "How do I quantize my playing?",
                "How do I export patterns to my DAW?"
            ])

        return suggestions[:10]  # Return top 10 suggestions