# --- 1. Librerías ---
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

# --- 2. Simulación de datos ---
np.random.seed(42)
n_samples = 500

data = pd.DataFrame({
    'libros_a_tiempo': np.random.randint(0, 50, n_samples),
    'libros_tarde': np.random.randint(0, 10, n_samples),
    'total_prestamos': np.random.randint(10, 100, n_samples),
    'multas_pagadas': np.random.randint(0, 5, n_samples),
    'tipo_usuario': np.random.choice(['estudiante', 'profesor', 'externo'], n_samples),
    'antiguedad_meses': np.random.randint(1, 120, n_samples),
    'historial_pagos': np.random.uniform(0, 1, n_samples),
    'sanciones': np.random.randint(0, 3, n_samples),
    'participacion_eventos': np.random.randint(0, 10, n_samples),
    'confiable': np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
})

# --- 3. Preprocesamiento ---
le = LabelEncoder()
data['tipo_usuario'] = le.fit_transform(data['tipo_usuario'])

X = data.drop(columns=['confiable'])
y = data['confiable']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 4. Pipeline + GridSearch + CV ---
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(random_state=42))
])

param_grid = {
    'clf__n_estimators': [100, 200],
    'clf__max_depth': [None, 10, 20],
    'clf__min_samples_split': [2, 5],
    'clf__min_samples_leaf': [1, 2]
}

grid_search = GridSearchCV(estimator=pipeline,
                           param_grid=param_grid,
                           cv=5,
                           n_jobs=-1,
                           verbose=2)

grid_search.fit(X_train, y_train)

print("Mejores hiperparámetros:", grid_search.best_params_)

# --- 5. Validación cruzada ---
cv_scores = cross_val_score(grid_search.best_estimator_, X_train, y_train, cv=5)
print(f"Cross-validated accuracy: {np.mean(cv_scores):.3f} ± {np.std(cv_scores):.3f}")

# --- 6. Evaluación en test ---
best_pipeline = grid_search.best_estimator_
y_pred = best_pipeline.predict(X_test)
y_proba = best_pipeline.predict_proba(X_test)[:,1]

print("Test accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# --- 7. Guardar modelo + LabelEncoder ---
joblib.dump(best_pipeline, 'modelo_confiabilidad_usuario_biblioteca.pkl')
joblib.dump(le, 'label_encoder_tipo_usuario.pkl')
