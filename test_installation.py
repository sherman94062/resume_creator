#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly
"""

import sys

def test_imports():
    """Test that all required libraries can be imported"""
    print("Testing installation...\n")

    tests = {
        "openai": "OpenAI API client",
        "markdown": "Markdown to HTML converter",
        "weasyprint": "PDF generator",
    }

    failed = []

    for module, description in tests.items():
        try:
            __import__(module)
            print(f"✓ {module:15} - {description}")
        except ImportError as e:
            print(f"✗ {module:15} - {description}")
            print(f"  Error: {e}")
            failed.append(module)

    print()

    if failed:
        print(f"❌ Installation incomplete. Missing: {', '.join(failed)}")
        print("\nTo fix:")
        print("  source venv/bin/activate")
        print("  pip install " + " ".join(failed))
        return False
    else:
        print("✅ All dependencies installed correctly!")

        # Check for API key
        import os
        if os.getenv("OPENAI_API_KEY"):
            print("✅ OPENAI_API_KEY environment variable is set")
        else:
            print("⚠️  OPENAI_API_KEY not set. You'll need to set it:")
            print("   export OPENAI_API_KEY='sk-...'")

        print("\n🚀 Ready to tailor resumes!")
        return True


def test_openai_version():
    """Check OpenAI library version"""
    try:
        import openai
        print(f"\nOpenAI library version: {openai.__version__}")

        # Check if it's the new version (1.0+)
        major_version = int(openai.__version__.split('.')[0])
        if major_version >= 1:
            print("✓ Using OpenAI library v1.0+ (correct version)")
        else:
            print("⚠️  Old OpenAI library detected. Consider upgrading:")
            print("   pip install --upgrade openai")
    except Exception as e:
        print(f"Could not check OpenAI version: {e}")


if __name__ == "__main__":
    success = test_imports()
    if success:
        test_openai_version()

    sys.exit(0 if success else 1)
