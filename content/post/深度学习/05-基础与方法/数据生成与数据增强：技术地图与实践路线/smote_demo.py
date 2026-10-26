from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score
from sklearn.model_selection import (
    StratifiedKFold, cross_validate, train_test_split,
)
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline

X, y = make_classification(
    n_samples=4000, n_features=12, n_informative=6,
    n_redundant=2, weights=[0.95, 0.05], random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42,
)

models = {
    "baseline": Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            solver="liblinear", max_iter=1000, random_state=42)),
    ]),
    "class_weight": Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            solver="liblinear", max_iter=1000, random_state=42,
            class_weight="balanced")),
    ]),
    "smote": Pipeline([
        ("scale", StandardScaler()),
        ("sample", SMOTE(random_state=42)),
        ("model", LogisticRegression(
            solver="liblinear", max_iter=1000, random_state=42)),
    ]),
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = {}
for name, model in models.items():
    result = cross_validate(
        model, X_train, y_train, cv=cv,
        scoring=["average_precision", "balanced_accuracy"],
    )
    cv_scores[name] = result["test_average_precision"].mean()
    print(name, {
        metric: round(float(result[f"test_{metric}"].mean()), 3)
        for metric in ["average_precision", "balanced_accuracy"]
    })

# 预先约定按交叉验证 AP 选方案，测试集只评估选中的方案。
best_name = max(cv_scores, key=cv_scores.get)
best = models[best_name].fit(X_train, y_train)
print("selected:", best_name)
print("test AP:", round(average_precision_score(
    y_test, best.predict_proba(X_test)[:, 1]), 3))
print("test balanced accuracy:", round(balanced_accuracy_score(
    y_test, best.predict(X_test)), 3))
