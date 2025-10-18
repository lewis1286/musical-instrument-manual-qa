import streamlit as st
import os
import tempfile
from typing import List, Dict
import pandas as pd
from pathlib import Path

from src.pdf_processor.pdf_extractor import PDFExtractor
from src.vector_db.chroma_manager import ChromaManager
from src.rag_pipeline.qa_system import MusicalInstrumentQA

class ManualQAInterface:
    """Streamlit interface for the Musical Instrument Manual Q&A system"""

    def __init__(self):
        self.init_session_state()
        self.init_components()

    def init_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'chroma_manager' not in st.session_state:
            st.session_state.chroma_manager = ChromaManager()

        if 'qa_system' not in st.session_state:
            try:
                st.session_state.qa_system = MusicalInstrumentQA(st.session_state.chroma_manager)
            except ValueError as e:
                st.session_state.qa_system = None
                st.session_state.openai_error = str(e)

        if 'pdf_extractor' not in st.session_state:
            st.session_state.pdf_extractor = PDFExtractor()

        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []

        if 'uploaded_manuals' not in st.session_state:
            st.session_state.uploaded_manuals = []

        if 'pending_manual' not in st.session_state:
            st.session_state.pending_manual = None

    def init_components(self):
        """Initialize UI components"""
        pass

    def render_sidebar(self):
        """Render the sidebar with manual management"""
        st.sidebar.header("📚 Manual Management")

        # Check if Anthropic API key is configured
        if st.session_state.qa_system is None:
            st.sidebar.error("⚠️ Anthropic API key not configured")
            st.sidebar.info("Please set your ANTHROPIC_API_KEY in the .env file")
            return

        # Upload new manual
        st.sidebar.subheader("Upload New Manual")

        # Show pending manual editor if we have one
        if st.session_state.pending_manual:
            self.render_manual_metadata_editor()
        else:
            uploaded_file = st.sidebar.file_uploader(
                "Choose a PDF manual",
                type=['pdf'],
                help="Upload synthesizer, keyboard, mixer, or other instrument manuals"
            )

            if uploaded_file is not None:
                if st.sidebar.button("Process Manual"):
                    self.process_uploaded_manual(uploaded_file)

        st.sidebar.divider()

        # Display uploaded manuals
        self.render_manual_list()

        st.sidebar.divider()

        # Database statistics
        self.render_database_stats()

        st.sidebar.divider()

        # Reset database section
        self.render_reset_section()

    def process_uploaded_manual(self, uploaded_file):
        """Process an uploaded PDF manual - Stage 1: Extract and analyze"""
        try:
            with st.spinner("Analyzing manual..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # Process the PDF to extract text and metadata
                chunks, metadata = st.session_state.pdf_extractor.process_manual(tmp_file_path)

                # Set the display name to the original filename (without .pdf)
                metadata.display_name = uploaded_file.name.replace('.pdf', '').replace('.PDF', '')

                # Store in session state for editing
                st.session_state.pending_manual = {
                    'chunks': chunks,
                    'metadata': metadata,
                    'tmp_file_path': tmp_file_path,
                    'original_filename': uploaded_file.name
                }

                st.sidebar.success(f"✅ Analyzed {uploaded_file.name}")
                st.rerun()

        except Exception as e:
            st.sidebar.error(f"Error processing manual: {str(e)}")

    def render_manual_metadata_editor(self):
        """Render the metadata editing form for pending manual"""
        pending = st.session_state.pending_manual
        metadata = pending['metadata']

        st.sidebar.subheader("📝 Review Manual Details")
        st.sidebar.write(f"**File:** {pending['original_filename']}")

        # Display Name
        display_name = st.sidebar.text_input(
            "Display Name",
            value=metadata.display_name,
            help="Name to show in search results and citations"
        )

        # Manufacturer - quick select + custom input
        st.sidebar.write("**Manufacturer**")
        manufacturer_suggestions = [
            "Custom/Other", "Moog", "Roland", "Korg", "Yamaha", "Nord", "Sequential", "Dave Smith",
            "Arturia", "Novation", "Akai", "Elektron", "Teenage Engineering",
            "Behringer", "Doepfer", "Make Noise", "Mutable Instruments",
            "Intellijel", "Expert Sleepers", "Focusrite", "PreSonus"
        ]

        current_manufacturer = metadata.manufacturer if metadata.manufacturer else ""

        # Quick select dropdown
        quick_select_index = 0  # Default to "Custom/Other"
        if current_manufacturer and current_manufacturer in manufacturer_suggestions:
            quick_select_index = manufacturer_suggestions.index(current_manufacturer)

        quick_select = st.sidebar.selectbox(
            "Quick select (or choose Custom/Other)",
            manufacturer_suggestions,
            index=quick_select_index
        )

        # Text input (pre-filled if not Custom/Other)
        if quick_select == "Custom/Other":
            manufacturer = st.sidebar.text_input(
                "Enter custom manufacturer",
                value=current_manufacturer if current_manufacturer not in manufacturer_suggestions[1:] else "",
                placeholder="e.g. Waldorf, Buchla, etc."
            )
        else:
            manufacturer = quick_select

        # Model
        model = st.sidebar.text_input(
            "Model",
            value=metadata.model if metadata.model else "",
            help="Model name or number"
        )

        # Instrument Type - quick select + custom input
        st.sidebar.write("**Instrument Type**")
        instrument_type_suggestions = [
            "custom/other", "synthesizer", "keyboard", "drum_machine", "mixer",
            "interface", "controller", "modular", "sampler", "effects",
            "sequencer", "delay", "reverb", "compressor", "eq", "vocoder", "filter"
        ]

        current_type = metadata.instrument_type if metadata.instrument_type else ""

        # Quick select dropdown
        type_quick_select_index = 0  # Default to "custom/other"
        if current_type and current_type in instrument_type_suggestions:
            type_quick_select_index = instrument_type_suggestions.index(current_type)

        type_quick_select = st.sidebar.selectbox(
            "Quick select (or choose custom/other)",
            instrument_type_suggestions,
            index=type_quick_select_index
        )

        # Text input (pre-filled if not custom/other)
        if type_quick_select == "custom/other":
            instrument_type = st.sidebar.text_input(
                "Enter custom instrument type",
                value=current_type if current_type not in instrument_type_suggestions[1:] else "",
                placeholder="e.g. arpeggiator, looper, etc."
            )
        else:
            instrument_type = type_quick_select

        st.sidebar.write(f"**Pages:** {metadata.total_pages}")
        st.sidebar.write(f"**Chunks:** {len(pending['chunks'])}")

        # Action buttons
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.sidebar.button("💾 Save Manual", type="primary"):
                self.save_manual_with_metadata(display_name, manufacturer, model, instrument_type)

        with col2:
            if st.sidebar.button("❌ Cancel"):
                self.cancel_manual_upload()

    def save_manual_with_metadata(self, display_name: str, manufacturer: str, model: str, instrument_type: str):
        """Save the manual with user-edited metadata"""
        try:
            pending = st.session_state.pending_manual

            # Update metadata with user inputs
            metadata = pending['metadata']
            metadata.display_name = display_name or metadata.display_name
            metadata.manufacturer = manufacturer or None
            metadata.model = model or None
            metadata.instrument_type = instrument_type or None

            # Update all chunks with the new metadata
            for chunk in pending['chunks']:
                chunk.metadata = metadata

            # Add to vector database
            st.session_state.chroma_manager.add_manual_chunks(pending['chunks'])

            # Clean up temporary file
            os.unlink(pending['tmp_file_path'])

            # Update uploaded manuals list
            st.session_state.uploaded_manuals = st.session_state.chroma_manager.get_all_manuals()

            # Clear pending manual
            st.session_state.pending_manual = None

            st.sidebar.success(f"✅ Saved {display_name}")
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Error saving manual: {str(e)}")

    def cancel_manual_upload(self):
        """Cancel the manual upload and clean up"""
        try:
            if st.session_state.pending_manual:
                # Clean up temporary file
                os.unlink(st.session_state.pending_manual['tmp_file_path'])

            # Clear pending manual
            st.session_state.pending_manual = None
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Error canceling upload: {str(e)}")

    def render_manual_list(self):
        """Render the list of uploaded manuals"""
        st.sidebar.subheader("Uploaded Manuals")

        manuals = st.session_state.chroma_manager.get_all_manuals()

        if not manuals:
            st.sidebar.info("No manuals uploaded yet")
            return

        for manual in manuals:
            display_title = manual.get('display_name', manual['filename'])[:30]
            with st.sidebar.expander(f"📖 {display_title}..."):
                st.write(f"**Display Name:** {manual.get('display_name', manual['filename'])}")
                st.write(f"**Manufacturer:** {manual['manufacturer']}")
                st.write(f"**Model:** {manual['model']}")
                st.write(f"**Type:** {manual['instrument_type']}")
                st.write(f"**Pages:** {manual['total_pages']}")
                st.write(f"**Chunks:** {manual['chunk_count']}")

                if st.button(f"Delete {display_title}", key=f"delete_{manual['filename']}"):
                    if st.session_state.chroma_manager.delete_manual(manual['filename']):
                        st.sidebar.success("Manual deleted")
                        st.rerun()

    def render_database_stats(self):
        """Render database statistics"""
        st.sidebar.subheader("Database Stats")

        stats = st.session_state.chroma_manager.get_database_stats()

        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Manuals", stats['total_manuals'])
        with col2:
            st.metric("Chunks", stats['total_chunks'])

        if stats['manufacturers']:
            st.sidebar.write("**Manufacturers:**")
            for manufacturer in stats['manufacturers'][:5]:  # Show top 5
                st.sidebar.write(f"• {manufacturer}")

        if stats['instrument_types']:
            st.sidebar.write("**Instrument Types:**")
            for inst_type in stats['instrument_types'][:5]:  # Show top 5
                st.sidebar.write(f"• {inst_type.replace('_', ' ').title()}")

    def render_reset_section(self):
        """Render the reset database section"""
        st.sidebar.subheader("🗑️ Reset Data")

        if st.sidebar.button("Reset All Data", type="secondary"):
            st.session_state.show_reset_confirmation = True

        # Show confirmation dialog
        if getattr(st.session_state, 'show_reset_confirmation', False):
            st.sidebar.warning("⚠️ This will delete ALL uploaded manuals and data!")
            st.sidebar.write("This action cannot be undone.")

            col1, col2 = st.sidebar.columns(2)

            with col1:
                if st.sidebar.button("✅ Confirm", type="primary"):
                    self.reset_all_data()

            with col2:
                if st.sidebar.button("❌ Cancel"):
                    st.session_state.show_reset_confirmation = False
                    st.rerun()

    def reset_all_data(self):
        """Reset all application data"""
        try:
            # Reset ChromaDB
            if st.session_state.chroma_manager.reset_database():
                # Clear session state
                st.session_state.conversation_history = []
                st.session_state.uploaded_manuals = []
                st.session_state.show_reset_confirmation = False

                # Clear QA system conversation memory
                if st.session_state.qa_system:
                    st.session_state.qa_system.clear_conversation()

                st.sidebar.success("✅ All data has been reset!")
                st.rerun()
            else:
                st.sidebar.error("❌ Failed to reset database")

        except Exception as e:
            st.sidebar.error(f"❌ Error resetting data: {str(e)}")

        st.session_state.show_reset_confirmation = False

    def render_main_content(self):
        """Render the main Q&A interface"""
        if st.session_state.qa_system is None:
            st.error("⚠️ Anthropic API key not configured. Please set ANTHROPIC_API_KEY in your .env file.")
            st.info("Copy .env.template to .env and add your Anthropic API key.")
            return

        # Quick start guide
        if not st.session_state.chroma_manager.get_all_manuals():
            st.info("👋 Welcome! Upload some instrument manuals using the sidebar to get started.")
            self.render_sample_questions()
            return

        # Main Q&A interface
        st.subheader("🎤 Ask a Question")

        # Query input
        query = st.text_input(
            "What would you like to know about your instruments?",
            placeholder="e.g., How do I connect my Moog to MIDI?",
            help="Ask questions about connections, specifications, presets, or any other topic covered in your manuals"
        )

        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)

            with col1:
                # Instrument type filter
                instrument_types = [''] + st.session_state.chroma_manager.get_unique_values('instrument_type')
                selected_instrument = st.selectbox(
                    "Filter by Instrument Type",
                    instrument_types,
                    help="Narrow search to specific instrument types"
                )

            with col2:
                # Manufacturer filter
                manufacturers = [''] + st.session_state.chroma_manager.get_unique_values('manufacturer')
                selected_manufacturer = st.selectbox(
                    "Filter by Manufacturer",
                    manufacturers,
                    help="Narrow search to specific manufacturers"
                )

            max_sources = st.slider("Max Sources", 1, 10, 5, help="Maximum number of manual sections to consider")

        # Submit button
        if st.button("Ask Question", type="primary") and query:
            self.handle_question(query, selected_instrument, selected_manufacturer, max_sources)

        # Display conversation history
        self.render_conversation_history()

        # Suggested questions
        self.render_suggested_questions()

    def handle_question(self, query: str, instrument_filter: str, manufacturer_filter: str, max_sources: int):
        """Handle a user question"""
        try:
            with st.spinner("Searching manuals..."):
                # Prepare filters
                filters = {}
                if instrument_filter:
                    filters['instrument_type'] = instrument_filter
                if manufacturer_filter:
                    filters['manufacturer'] = manufacturer_filter

                # Get answer
                response = st.session_state.qa_system.answer_question(query, max_sources)

                # Display answer
                st.subheader("💬 Answer")
                st.write(response.answer)

                # Display sources
                if response.sources:
                    st.subheader("📖 Sources")
                    for i, source in enumerate(response.sources):
                        display_name = source.get('display_name', source['filename'])
                        with st.expander(f"Source {i+1}: {display_name} (Page {source['page_number']})"):
                            st.write(f"**Manual:** {display_name}")
                            st.write(f"**Manufacturer:** {source['manufacturer']}")
                            st.write(f"**Model:** {source['model']}")
                            st.write(f"**Section:** {source['section_type']}")
                            st.write(f"**Content Preview:**")
                            st.write(source['content_preview'])

                # Add to conversation history
                st.session_state.conversation_history.append({
                    'question': query,
                    'answer': response.answer,
                    'sources': len(response.sources)
                })

        except Exception as e:
            st.error(f"Error processing question: {str(e)}")

    def render_conversation_history(self):
        """Render the conversation history"""
        if not st.session_state.conversation_history:
            return

        st.subheader("💭 Conversation History")

        for i, exchange in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
            with st.expander(f"Q{len(st.session_state.conversation_history)-i}: {exchange['question'][:50]}..."):
                st.write(f"**Question:** {exchange['question']}")
                st.write(f"**Answer:** {exchange['answer']}")
                st.write(f"**Sources:** {exchange['sources']}")

        if len(st.session_state.conversation_history) > 5:
            st.info(f"Showing latest 5 of {len(st.session_state.conversation_history)} conversations")

        if st.button("Clear History"):
            st.session_state.conversation_history = []
            if st.session_state.qa_system:
                st.session_state.qa_system.clear_conversation()
            st.rerun()

    def render_suggested_questions(self):
        """Render suggested questions"""
        st.subheader("💡 Suggested Questions")

        # Get suggestions based on available instrument types
        instrument_types = st.session_state.chroma_manager.get_unique_values('instrument_type')
        suggestions = []

        if instrument_types:
            # Get suggestions for the first available instrument type
            suggestions = st.session_state.qa_system.suggest_questions(instrument_types[0])
        else:
            suggestions = st.session_state.qa_system.suggest_questions()

        # Display as buttons
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions[:6]):  # Show 6 suggestions
            col = cols[i % 2]
            if col.button(suggestion, key=f"suggestion_{i}"):
                st.session_state.suggested_query = suggestion
                st.rerun()

    def render_sample_questions(self):
        """Render sample questions for new users"""
        st.subheader("💡 Example Questions You Can Ask")

        sample_questions = [
            "How do I set up MIDI connections?",
            "What are the audio input specifications?",
            "How do I save presets?",
            "How do I connect to my computer?",
            "What is the power consumption?",
            "How do I perform a factory reset?",
            "How do the filters work?",
            "How do I use the arpeggiator?",
            "How do I set up CV/Gate connections?",
            "How do I sync to external clock?"
        ]

        for question in sample_questions:
            st.write(f"• {question}")

    def render(self):
        """Render the complete interface"""
        # Render sidebar
        self.render_sidebar()

        # Render main content
        self.render_main_content()