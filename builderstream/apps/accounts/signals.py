"""Account signals.

Registration side-effects (OWNER membership creation, module activation)
are handled by tenants/signals.py::setup_new_organization which fires
on Organization post_save.

Email operations are handled asynchronously via Celery tasks in tasks.py.
"""
