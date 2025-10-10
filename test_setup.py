#!/usr/bin/env python3
"""
Test script to verify the Musical Instrument Manual Q&A system setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_poetry():
    """Check if Poetry is installed and available"""
    try:
        result = subprocess.run(['poetry', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Poetry: {result.stdout.strip()}")
            return True
        else:
            print("❌ Poetry not working properly")
            return False
    except FileNotFoundError:
        print("❌ Poetry not found - install from https://python-poetry.org/")
        return False

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")

    try:
        import streamlit
        print("✅ Streamlit")
    except ImportError:
        print("❌ Streamlit - run: poetry install")
        return False

    try:
        import chromadb
        print("✅ ChromaDB")
    except ImportError:
        print("❌ ChromaDB - run: poetry install")
        return False

    try:
        import PyPDF2
        print("✅ PyPDF2")
    except ImportError:
        print("❌ PyPDF2 - run: poetry install")
        return False

    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF")
    except ImportError:
        print("❌ PyMuPDF - run: poetry install")
        return False

    try:
        import langchain
        print("✅ LangChain")
    except ImportError:
        print("❌ LangChain - run: poetry install")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError:
        print("❌ python-dotenv - run: poetry install")
        return False

    return True

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")

    # Check .env file
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        if os.path.exists('.env.template'):
            print("   Copy .env.template to .env and add your OpenAI API key")
        return False
    else:
        print("✅ .env file exists")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Check OpenAI API key
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not found in .env file")
        return False

    return True

def test_directories():
    """Test that required directories exist"""
    print("\nTesting directories...")

    required_dirs = ['src', 'src/pdf_processor', 'src/vector_db', 'src/rag_pipeline', 'src/ui']

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            return False

    return True

def test_modules():
    """Test that our modules can be imported"""
    print("\nTesting custom modules...")

    try:
        from src.pdf_processor.pdf_extractor import PDFExtractor
        print("✅ PDF Extractor")
    except ImportError as e:
        print(f"❌ PDF Extractor: {e}")
        return False

    try:
        from src.vector_db.chroma_manager import ChromaManager
        print("✅ Chroma Manager")
    except ImportError as e:
        print(f"❌ Chroma Manager: {e}")
        return False

    try:
        from src.rag_pipeline.qa_system import MusicalInstrumentQA
        print("✅ QA System")
    except ImportError as e:
        print(f"❌ QA System: {e}")
        return False

    try:
        from src.ui.main_interface import ManualQAInterface
        print("✅ Main Interface")
    except ImportError as e:
        print(f"❌ Main Interface: {e}")
        return False

    return True

def main():
    """Run all tests"""
    print("🎹 Musical Instrument Manual Q&A System - Setup Test")
    print("=" * 60)

    all_passed = True

    # Check Poetry first
    all_passed &= check_poetry()

    # Run tests
    all_passed &= test_imports()
    all_passed &= test_environment()
    all_passed &= test_directories()
    all_passed &= test_modules()

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("Run the application with: poetry run streamlit run app.py")
        print("Or use the quick start script: ./run.sh")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("Try running: poetry install")
        sys.exit(1)

if __name__ == "__main__":
    main()