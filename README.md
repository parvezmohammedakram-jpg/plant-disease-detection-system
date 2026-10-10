# AI Plant Disease Detection System

A production-grade, modular web application designed to help farmers and gardeners identify plant diseases using Artificial Intelligence. Built with Flask, MongoDB, and TensorFlow, this platform provides actionable treatment plans, tracks plant health over time, and manages daily agricultural tasks.

---

## 🌟 Key Features

*   **AI Disease Detection**: Upload an image of a plant leaf and receive an instant prediction of the crop type and potential disease using a Convolutional Neural Network (CNN).
*   **Demo / Fallback Mode**: If the TensorFlow model isn't downloaded, the system gracefully falls back to a simulated demo mode, allowing testing without large model weights.
*   **Disease Knowledge Base**: Structured repository of plant diseases mapping to organic, chemical, and preventive treatment plans.
*   **Plant Profiles**: Create and track specific crops (e.g., "Greenhouse Tomato #1").
*   **Care Logging & Reminders**: Log treatments applied to individual plants and schedule follow-up tasks to stay on top of farm maintenance.
*   **Secure Authentication**: Role-based access control, hashed passwords, session timeouts, and full CSRF protection across all forms.
*   **Structured Logging & Error Handling**: Production-ready JSON logging and centralized, user-friendly error pages.

## 🏗️ Architecture

The system uses a **Flask Application Factory** pattern to ensure clean separation of concerns:

```text
plant-disease-detection-system/
├── app/
│   ├── admin/             # Admin dashboard & user management
│   ├── auth/              # Registration, login, and password resets
│   ├── disease_knowledge/ # Disease and treatment database lookups
│   ├── main/              # Landing page and user dashboard
│   ├── ml/                # TensorFlow model loading and inference
│   ├── plants/            # User plant profiles and care history
│   ├── predictions/       # Image upload and detection routes
│   └── reminders/         # Task scheduling
├── docs/                  # Project specifications and ADRs
├── models/                # ML weights (e.g. model_weights.h5)
├── scripts/               # DB seed scripts and utilities
├── static/                # CSS, JS, and Images
├── templates/             # Jinja2 HTML templates
├── uploads/               # User-uploaded leaf images
└── run.py                 # Application entry point
```

## 🛠️ Tech Stack

*   **Backend Framework**: Python / Flask (v2.3)
*   **Database**: MongoDB (PyMongo)
*   **Machine Learning**: TensorFlow / Keras, NumPy, Pillow
*   **Frontend**: HTML5, Vanilla CSS, Bootstrap 5.3, FontAwesome
*   **Security**: Flask-WTF (CSRF), bcrypt, itsdangerous (Token generation)

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.9+
*   MongoDB (running locally on default port `27017` or via Atlas)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/plant-disease-detection-system.git
cd plant-disease-detection-system
```

### 2. Set up the virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```ini
APP_ENV=development
SECRET_KEY=your-super-secret-key-here
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=plant_disease_db
LOG_LEVEL=INFO
```

### 5. Seed the Database
Run the provided script to populate the initial disease knowledge base and treatments:
```bash
python scripts/seed_diseases.py
```

### 6. Add the ML Model (Optional)
To use actual AI predictions rather than Demo Mode, place your trained Keras model inside the `models/` directory:
```bash
# Path should be: models/model_weights.h5
```

### 7. Run the Application
```bash
python run.py
```
The application will be available at `http://127.0.0.1:5000`.

## 📜 Development Roadmap (Implementation Plan)

- [x] Phase 1: Foundation (App Factory, Blueprints, MongoDB Integration)
- [x] Phase 2: Core ML (ModelManager singleton, demo mode)
- [x] Phase 3: Auth Hardening (CSRF, token-based password resets)
- [x] Phase 4: Farmer History (Plant profiles, filtering)
- [x] Phase 5: Treatment & Follow-up (Task scheduling, reminders)
- [ ] Phase 6: Analytics & Dashboard
- [ ] Phase 7: Geolocation & Weather
- [ ] Phase 8: Advanced UX (AJAX forms, lazy loading)
- [ ] Phase 9: Community & Reviews
- [ ] Phase 10: Offline Mode (PWA)
- [ ] Phase 11: Admin Portal
- [ ] Phase 12: Hardening & Deployment (Docker, CI/CD)

## 📄 License
This project is for educational and research purposes.
