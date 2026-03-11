"""
Document service layer.
Business logic for document management, delegates to version_dal.
"""

from modules.sys_admin.dal import version_dal


def list_documents(path):
    """List files and subdirectories."""
    return version_dal.list_documents(path)


def read_document(path):
    """Read document content with version info."""
    return version_dal.read_document(path)


def save_document(path, content, author='管理员'):
    """Save document with auto version increment."""
    return version_dal.save_document(path, content, author)


def create_document(path, content='', author='管理员'):
    """Create a new document."""
    return version_dal.create_document(path, content, author)


def delete_document(path):
    """Delete a document."""
    return version_dal.delete_document(path)
