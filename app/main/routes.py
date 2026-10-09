"""
Main pages routes.
"""
from flask import render_template, session
from . import main_bp
from ..utils.decorators import login_required
from ..extensions import get_db

@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    db = get_db()
    predictions_col = db['predictions']
    
    recent_predictions = list(
        predictions_col.find({'user_id': user_id})
        .sort('created_at', -1)
        .limit(5)
    )
    total_predictions = predictions_col.count_documents({'user_id': user_id})
    
    return render_template(
        'dashboard.html',
        predictions=recent_predictions,
        total_predictions=total_predictions,
    )
