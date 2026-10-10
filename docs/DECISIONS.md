# Architectural Decisions Record (ADR)

## DECISION 1: Monolithic Modular Architecture
- **Date**: [Current Date]
- **Context**: The existing app is a single `app.py` script. The system needs to scale to support weather, user tracking, and admin features.
- **Decision**: Refactor into a modular monolith using Flask Blueprints rather than splitting into microservices.
- **Rationale**: Microservices introduce unnecessary operational complexity (networking, separate deployments, distributed tracing) for a project of this size. A modular monolith provides the code organization benefits without the operational overhead.

## DECISION 2: Database Engine - MongoDB
- **Date**: [Current Date]
- **Context**: The existing app uses MongoDB. The data model involves highly variable structured data (treatments have different fields, risk rules vary).
- **Decision**: Retain MongoDB. Do not migrate to a relational database (SQL).
- **Rationale**: The dynamic nature of ML predictions, disease data, and risk rules maps well to a NoSQL document store. Migrating to SQL would provide no immediate benefit and delay feature development.

## DECISION 3: ML Abstraction Layer (ModelManager)
- **Date**: [Current Date]
- **Context**: TensorFlow models are heavy and slow to load. Loading them per-request or in global scope randomly causes memory leaks.
- **Decision**: Implement a singleton `ModelManager` class loaded explicitly on app startup (or first request). It must support a "demo mode".
- **Rationale**: Controls memory usage, allows for graceful degradation if the `.h5` file is missing, and makes unit testing the web layer easier (by mocking the manager).

## DECISION 4: No ML Retraining
- **Date**: [Current Date]
- **Context**: The prompt requests a robust system, but the ML model only supports specific classes and lacks severity data.
- **Decision**: Explicitly rule out modifying, retraining, or simulating AI capabilities the model doesn't possess.
- **Rationale**: "Never fake AI" is a core tenet. The platform must be built *around* the existing model's constraints, not by hallucinating capabilities.
