"""
Admin routes.
"""
from flask import render_template
from . import admin_bp
from ..utils.decorators import admin_required


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard placeholder."""
    return render_template('admin/dashboard.html')
