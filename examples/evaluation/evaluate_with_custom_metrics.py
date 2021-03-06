from sklearn.linear_model import LinearRegression
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
import numpy as np
import mlflow

cali_housing = fetch_california_housing(as_frame=True)

X_train, X_test, y_train, y_test = train_test_split(
    cali_housing.data, cali_housing.target, test_size=0.2, random_state=123
)

lin_reg = LinearRegression()
lin_reg.fit(X_train, y_train)

eval_data = X_test.copy()
eval_data["target"] = y_test


def example_custom_metric_fn(eval_df, builtin_metrics):
    return {
        "squared_diff_plus_one": np.sum(np.abs(eval_df["prediction"] - eval_df["target"] + 1) ** 2),
        "sum_on_label_divided_by_two": builtin_metrics["sum_on_label"] / 2,
    }


with mlflow.start_run() as run:
    mlflow.sklearn.log_model(lin_reg, "model")
    model_uri = mlflow.get_artifact_uri("model")
    result = mlflow.evaluate(
        model=model_uri,
        data=eval_data,
        targets="target",
        model_type="regressor",
        dataset_name="cali_housing",
        evaluators=["default"],
        custom_metrics=[example_custom_metric_fn],
    )

print(f"metrics:\n{result.metrics}")
