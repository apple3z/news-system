"""
Version/document data access layer.
Wraps version_manager.py functions for document file I/O and versioning.
"""

import sys
import os

# Ensure project root is in path so version_manager can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from version_manager import (
    list_documents as _list_documents,
    read_document as _read_document,
    save_document as _save_document,
    create_document as _create_document,
    delete_document as _delete_document,
)


def list_documents(path):
    """List files and subdirectories at the given path."""
    return _list_documents(path)


def read_document(path):
    """Read document content with version info."""
    return _read_document(path)


def save_document(path, content, author='管理员'):
    """Save document content with auto version increment."""
    return _save_document(path, content, author)


def create_document(path, content='', author='管理员'):
    """Create a new document."""
    return _create_document(path, content, author)


def delete_document(path):
    """Delete a document."""
    return _delete_document(path)
