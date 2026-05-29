"""Thread-local tenant context for multi-tenant isolation."""
import threading
from contextlib import contextmanager

_thread_locals = threading.local()


def set_current_organization(organization):
    """Set the current organization in thread-local storage."""
    _thread_locals.organization = organization


def get_current_organization():
    """Get the current organization from thread-local storage."""
    return getattr(_thread_locals, "organization", None)


def clear_current_organization():
    """Clear the current organization from thread-local storage."""
    _thread_locals.organization = None


@contextmanager
def tenant_context(organization):
    """Context manager for setting tenant context.

    Use in Celery tasks and management commands:

        with tenant_context(org):
            # All TenantModel queries are scoped to org
            projects = Project.objects.all()
    """
    previous = get_current_organization()
    set_current_organization(organization)
    try:
        yield organization
    finally:
        if previous is not None:
            set_current_organization(previous)
        else:
            clear_current_organization()
