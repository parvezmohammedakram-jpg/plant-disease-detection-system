"""
Predictions routes.
"""
from datetime import datetime, timezone
from bson.objectid import ObjectId
from flask import render_template, request, redirect, url_for, session, flash, current_app, send_from_directory

from . import predictions_bp
from ..extensions import get_db
from ..utils.decorators import login_required
from ..utils.validation import validate_image_upload

# Temporary mock for ML (until Phase 2 is fully implemented)
# We will use the existing predict_disease function logic or move it to ml package.

@predictions_bp.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    if request.method == 'POST':
        try:
            filepath, filename = validate_image_upload(request.files.get('leaf_image'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('detect.html')

        try:
            # We will refactor to use ModelManager in Phase 2
            # For now, we will do a simple mock prediction to keep the flow working
            # as it was in the base app before we move all ML logic to ml/ package
            
            import random
            CLASS_LABELS = [
                'Pepper__bell___Bacterial_spot',
                'Pepper__bell___healthy',
                'Potato___Early_blight',
                'Potato___Late_blight',
                'Potato___healthy',
            ]
            
            predicted_class = CLASS_LABELS[random.randint(0, len(CLASS_LABELS) - 1)]
            confidence = round(random.uniform(0.70, 0.99), 4)
            all_predictions = {c: round(random.uniform(0.01, 0.1), 4) for c in CLASS_LABELS}
            
            CLASS_DISPLAY_NAMES = {
                'Pepper__bell___Bacterial_spot': 'Pepper Bell - Bacterial Spot',
                'Pepper__bell___healthy': 'Pepper Bell - Healthy',
                'Potato___Early_blight': 'Potato - Early Blight',
                'Potato___Late_blight': 'Potato - Late Blight',
                'Potato___healthy': 'Potato - Healthy',
            }
            display_name = CLASS_DISPLAY_NAMES.get(predicted_class, predicted_class)
            disease_info = {
                'disease': display_name,
                'crop': 'Unknown',
                'description': 'Temporary mock data.',
                'symptoms': ['Mock symptom'],
                'treatment': ['Mock treatment']
            }

            db = get_db()
            predictions_col = db['predictions']
            
            prediction_record = {
                'user_id': session['user_id'],
                'image_filename': filename,
                'predicted_class': predicted_class,
                'display_name': display_name,
                'confidence': confidence,
                'all_predictions': all_predictions,
                'disease_info': disease_info,
                'created_at': datetime.now(timezone.utc),
            }
            result = predictions_col.insert_one(prediction_record)
            prediction_id = str(result.inserted_id)

            return redirect(url_for('predictions.result', prediction_id=prediction_id))
            
        except Exception as e:
            current_app.logger.error("Detection failed: %s", e)
            flash(f'Prediction failed: {str(e)}', 'error')
            return render_template('detect.html')

    return render_template('detect.html')


@predictions_bp.route('/result/<prediction_id>')
@login_required
def result(prediction_id):
    db = get_db()
    try:
        prediction = db['predictions'].find_one({
            '_id': ObjectId(prediction_id),
            'user_id': session['user_id'],
        })
    except Exception:
        flash('Invalid prediction ID.', 'error')
        return redirect(url_for('predictions.history'))

    if not prediction:
        flash('Prediction not found.', 'error')
        return redirect(url_for('predictions.history'))

    return render_template('result.html', prediction=prediction)


@predictions_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 10

    db = get_db()
    predictions_col = db['predictions']

    total = predictions_col.count_documents({'user_id': user_id})
    predictions = list(
        predictions_col.find({'user_id': user_id})
        .sort('created_at', -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'history.html',
        predictions=predictions,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@predictions_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_DIR'], filename)
