"""
Regression Models - Multiple regression model types with diagnostics.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import cross_val_score
import statsmodels.api as sm
from utils.theme import inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
from utils.components import kpi_row, section_header, stat_card, info_banner, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, get_numeric_columns


data = load_data()

PREDICTOR_VARS = [
    "poverty_rate", "unemployment_rate", "median_income", "cost_per_meal",
    "snap_rate", "population", "hs_or_less", "gini",
    "weighted_annual_food_budget_shortfall",
]
available_predictors = [v for v in PREDICTOR_VARS if v in data.columns]

MODEL_TYPES = {
    "linear": "Linear Regression (OLS)",
    "poly2": "Polynomial Regression (Degree 2)",
    "poly3": "Polynomial Regression (Degree 3)",
    "ridge": "Ridge Regression (L2)",
    "lasso": "LASSO Regression (L1)",
    "elasticnet": "Elastic Net",
    "random_forest": "Random Forest",
}

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Model Configuration</p>', unsafe_allow_html=True)

    all_vars = get_numeric_columns(data)
    default_idx = all_vars.index("overall_food_insecurity_rate") if "overall_food_insecurity_rate" in all_vars else 0
    dep_var = st.selectbox(
        "Dependent Variable",
        all_vars,
        index=default_idx,
        format_func=get_variable_label,
    )

    model_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                           int(data["year"].max()))

    model_type = st.selectbox("Model Type", list(MODEL_TYPES.keys()),
                              format_func=lambda k: MODEL_TYPES[k])

    selected_predictors = st.multiselect(
        "Independent Variables",
        available_predictors,
        default=available_predictors[:4],
        format_func=get_variable_label,
    )

    scale_data = st.checkbox("Standardize Variables", value=False)

page_header("Regression Models",
            f"Build and evaluate {MODEL_TYPES.get(model_type, 'regression')} models", "chart-line")

if not selected_predictors:
    info_banner("Select at least one independent variable to build a model.", "warning")
    st.stop()

# Prepare data
model_data = data[data["year"] == model_year][[dep_var] + selected_predictors].dropna()

if len(model_data) < 10:
    info_banner("Insufficient data to build model. Try different year or variables.", "warning")
    st.stop()

X = model_data[selected_predictors].values
y = model_data[dep_var].values

if scale_data:
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

# Build model
run_model = st.button("Build Model", type="primary", width='stretch')

if run_model or "reg_results" in st.session_state:
    if run_model:
        if model_type == "linear":
            model = LinearRegression()
        elif model_type == "poly2":
            poly = PolynomialFeatures(degree=2, include_bias=False)
            X = poly.fit_transform(X)
            model = LinearRegression()
        elif model_type == "poly3":
            poly = PolynomialFeatures(degree=3, include_bias=False)
            X = poly.fit_transform(X)
            model = LinearRegression()
        elif model_type == "ridge":
            model = Ridge(alpha=1.0)
        elif model_type == "lasso":
            model = Lasso(alpha=0.01)
        elif model_type == "elasticnet":
            model = ElasticNet(alpha=0.01, l1_ratio=0.5)
        elif model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        else:
            model = LinearRegression()

        model.fit(X, y)
        y_pred = model.predict(X)

        r2 = r2_score(y, y_pred)
        n, p = X.shape
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else r2
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)

        # OLS summary for linear models
        ols_summary = None
        if model_type == "linear":
            X_sm = sm.add_constant(model_data[selected_predictors].values)
            ols_model = sm.OLS(y, X_sm).fit()
            ols_summary = ols_model

        # Cross-validation
        cv_model = LinearRegression() if model_type in ["linear", "poly2", "poly3"] else model.__class__(**model.get_params())
        try:
            cv_scores = cross_val_score(cv_model, X, y, cv=min(5, len(y) // 2), scoring="r2")
            cv_r2 = cv_scores.mean()
        except Exception:
            cv_r2 = None

        st.session_state["reg_results"] = {
            "model": model, "y": y, "y_pred": y_pred,
            "r2": r2, "adj_r2": adj_r2, "rmse": rmse, "mae": mae,
            "cv_r2": cv_r2, "n": n, "p": p, "ols_summary": ols_summary,
        }

    res = st.session_state["reg_results"]

    # Metrics KPIs
    kpi_row([
        {"title": "R²", "value": f"{res['r2']:.4f}", "icon": "bullseye", "gradient": "sapphire"},
        {"title": "Adjusted R²", "value": f"{res['adj_r2']:.4f}", "icon": "adjust", "gradient": "navy"},
        {"title": "RMSE", "value": f"{res['rmse']:.4f}", "icon": "ruler", "gradient": "amber"},
        {"title": "MAE", "value": f"{res['mae']:.4f}", "icon": "arrows-alt-h", "gradient": "amethyst"},
    ])

    st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

    # LLM Insight Engine
    context_dict = {
        "Year": model_year,
        "Model Type": MODEL_TYPES.get(model_type, model_type),
        "Dependent Variable (Target)": get_variable_label(dep_var),
        "Predictors": [get_variable_label(v) for v in selected_predictors],
        "R-Squared": f"{res['r2']:.4f}",
        "RMSE": f"{res['rmse']:.4f}",
        "Observations (n)": f"{res['n']:,}"
    }
    llm_explainer_ui("Regression Models", context_dict)

    # Fitted vs Actual
    col1, col2 = st.columns(2)

    with col1:
        section_header("Fitted vs Actual", icon="crosshairs")
        fig_fit = go.Figure()
        fig_fit.add_trace(go.Scatter(
            x=res["y"], y=res["y_pred"],
            mode="markers",
            marker=dict(color=COLORS["sapphire"], opacity=0.5, size=5),
            name="Predictions",
            hovertemplate="Actual: %{x:.3f}<br>Predicted: %{y:.3f}<extra></extra>",
        ))
        # Perfect fit line
        min_v, max_v = min(res["y"].min(), res["y_pred"].min()), max(res["y"].max(), res["y_pred"].max())
        fig_fit.add_trace(go.Scatter(
            x=[min_v, max_v], y=[min_v, max_v],
            mode="lines", line=dict(color=COLORS["ruby"], dash="dash", width=2),
            name="Perfect Fit",
        ))
        fig_fit.update_layout(
            **PLOTLY_LAYOUT, title="", height=400,
            xaxis_title="Actual", yaxis_title="Predicted",
            showlegend=True,
        )
        st.plotly_chart(fig_fit, width='stretch')

    with col2:
        section_header("Residual Distribution", icon="chart-area")
        residuals = res["y"] - res["y_pred"]
        fig_res = px.histogram(
            x=residuals, nbins=40,
            color_discrete_sequence=[COLORS["amethyst"]],
            labels={"x": "Residual"},
        )
        fig_res.update_layout(
            **PLOTLY_LAYOUT, title="", height=400,
            xaxis_title="Residual", yaxis_title="Frequency",
        )
        st.plotly_chart(fig_res, width='stretch')

    # Coefficient plot (for linear models)
    if model_type in ["linear", "ridge", "lasso", "elasticnet"] and hasattr(res["model"], "coef_"):
        section_header("Coefficient Plot", icon="sliders-h")
        coefs = pd.DataFrame({
            "Variable": [get_variable_label(v) for v in selected_predictors],
            "Coefficient": res["model"].coef_,
        }).sort_values("Coefficient")

        fig_coef = px.bar(
            coefs, x="Coefficient", y="Variable", orientation="h",
            color="Coefficient",
            color_continuous_scale=[[0, COLORS["ruby"]], [0.5, COLORS["pearl"]], [1, COLORS["sapphire"]]],
            color_continuous_midpoint=0,
        )
        fig_coef.update_layout(
            **PLOTLY_LAYOUT, title="", height=max(300, len(selected_predictors) * 40),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_coef, width='stretch')

    # Feature importance for RF
    if model_type == "random_forest":
        section_header("Feature Importance", icon="sort-amount-down")
        importances = pd.DataFrame({
            "Variable": [get_variable_label(v) for v in selected_predictors],
            "Importance": res["model"].feature_importances_,
        }).sort_values("Importance", ascending=True)

        fig_imp = px.bar(
            importances, x="Importance", y="Variable", orientation="h",
            color_discrete_sequence=[COLORS["emerald"]],
        )
        fig_imp.update_layout(
            **PLOTLY_LAYOUT, title="", height=max(300, len(selected_predictors) * 40),
        )
        st.plotly_chart(fig_imp, width='stretch')

    # OLS Summary
    if res["ols_summary"] is not None:
        section_header("OLS Model Summary", icon="file-alt")
        st.code(res["ols_summary"].summary().as_text(), language=None)

    # Model info
    section_header("Model Information", icon="info-circle")
    cv_text = f"{res['cv_r2']:.4f}" if res["cv_r2"] is not None else "N/A"
    st.markdown(
        f"""
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div class="grid grid-cols-3 gap-4 text-sm">
                <div>
                    <p class="text-gray-500 font-semibold">Model Type</p>
                    <p class="text-gray-800">{MODEL_TYPES.get(model_type, model_type)}</p>
                </div>
                <div>
                    <p class="text-gray-500 font-semibold">Observations</p>
                    <p class="text-gray-800">{res['n']:,}</p>
                </div>
                <div>
                    <p class="text-gray-500 font-semibold">Cross-Validated R²</p>
                    <p class="text-gray-800">{cv_text}</p>
                </div>
                <div>
                    <p class="text-gray-500 font-semibold">Dependent Variable</p>
                    <p class="text-gray-800">{get_variable_label(dep_var)}</p>
                </div>
                <div>
                    <p class="text-gray-500 font-semibold">Predictors</p>
                    <p class="text-gray-800">{res['p']}</p>
                </div>
                <div>
                    <p class="text-gray-500 font-semibold">Year</p>
                    <p class="text-gray-800">{model_year}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
