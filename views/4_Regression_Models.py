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
from utils.theme import enforce_landscape_on_mobile, inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
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

enforce_landscape_on_mobile()
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

    # Build model-type specific context for LLM
    context_dict = {
        "Year": model_year,
        "Model Type": MODEL_TYPES.get(model_type, model_type),
        "Dependent Variable (Target)": get_variable_label(dep_var),
        "Independent Variables": ", ".join([get_variable_label(v) for v in selected_predictors]),
        "R-Squared": f"{res['r2']:.4f}",
        "Adjusted R-Squared": f"{res['adj_r2']:.4f}",
        "RMSE": f"{res['rmse']:.4f}",
        "MAE": f"{res['mae']:.4f}",
        "Cross-Validated R²": f"{res['cv_r2']:.4f}" if res['cv_r2'] is not None else "N/A",
        "Observations (n)": f"{res['n']:,}",
        "Number of Predictors": f"{res['p']}",
    }
    if res["ols_summary"] is not None:
        ols = res["ols_summary"]
        context_dict["F-Statistic"] = f"{ols.fvalue:.2f}"
        context_dict["Prob(F-statistic)"] = f"{ols.f_pvalue:.2e}"
        context_dict["AIC"] = f"{ols.aic:.2f}"
        context_dict["BIC"] = f"{ols.bic:.2f}"
        context_dict["Durbin-Watson"] = f"{ols.durbin_watson:.3f}" if hasattr(ols, 'durbin_watson') else "N/A"
        # Add individual coefficient p-values
        pvals = ols.pvalues[1:]  # skip const
        sig_vars = [get_variable_label(v) for v, p in zip(selected_predictors, pvals) if p < 0.05]
        insig_vars = [get_variable_label(v) for v, p in zip(selected_predictors, pvals) if p >= 0.05]
        context_dict["Statistically Significant Predictors (p<0.05)"] = ", ".join(sig_vars) if sig_vars else "None"
        context_dict["Insignificant Predictors"] = ", ".join(insig_vars) if insig_vars else "None"
    if model_type == "random_forest":
        importances = dict(zip([get_variable_label(v) for v in selected_predictors],
                               res["model"].feature_importances_))
        top3 = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:3]
        context_dict["Top 3 Feature Importances"] = ", ".join([f"{k}: {v:.3f}" for k, v in top3])
    llm_explainer_ui("Regression Models", context_dict)

    # Fitted vs Actual
    col1, col2 = st.columns(2)

    with col1:
        section_header("Fitted vs Actual", icon="crosshairs")
        fig_fit = go.Figure()
        fig_fit.add_trace(go.Scatter(
            x=res["y"], y=res["y_pred"],
            mode="markers",
            marker=dict(color=COLORS["blue"], opacity=0.5, size=5),
            name="Predictions",
            hovertemplate="Actual: %{x:.3f}<br>Predicted: %{y:.3f}<extra></extra>",
        ))
        # Perfect fit line
        min_v, max_v = min(res["y"].min(), res["y_pred"].min()), max(res["y"].max(), res["y_pred"].max())
        fig_fit.add_trace(go.Scatter(
            x=[min_v, max_v], y=[min_v, max_v],
            mode="lines", line=dict(color=COLORS["rose"], dash="dash", width=2),
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
            color_discrete_sequence=[COLORS["violet"]],
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
            color_continuous_scale=[[0, COLORS["rose"]], [0.5, COLORS["pearl"]], [1, COLORS["blue"]]],
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
            color_discrete_sequence=[COLORS["teal"]],
        )
        fig_imp.update_layout(
            **PLOTLY_LAYOUT, title="", height=max(300, len(selected_predictors) * 40),
        )
        st.plotly_chart(fig_imp, width='stretch')

    # OLS Summary — side-by-side with LLM interpretation
    if res["ols_summary"] is not None:
        section_header("OLS Model Summary", icon="file-alt")
        sum_col, interp_col = st.columns([1.1, 0.9])

        with sum_col:
            st.code(res["ols_summary"].summary().as_text(), language=None)

        with interp_col:
            from utils.llm import generate_insights

            # Build a model-type-specific interpretation prompt
            ols = res["ols_summary"]
            pvals = ols.pvalues[1:]
            coefs = ols.params[1:]
            sig_pairs = [(get_variable_label(v), c, p)
                         for v, c, p in zip(selected_predictors, coefs, pvals)]
            sig_text = "; ".join(
                [f"{name}: coef={coef:.4f}, p={pv:.3f}" for name, coef, pv in sig_pairs]
            )

            interp_context = {
                "Model": "OLS Ordinary Least Squares Regression",
                "Target Variable": get_variable_label(dep_var),
                "Year": model_year,
                "R-Squared": f"{res['r2']:.4f}",
                "Adjusted R-Squared": f"{res['adj_r2']:.4f}",
                "F-Statistic": f"{ols.fvalue:.2f}",
                "Prob(F-statistic)": f"{ols.f_pvalue:.2e}",
                "AIC": f"{ols.aic:.2f}",
                "BIC": f"{ols.bic:.2f}",
                "Observations": f"{res['n']:,}",
                "Predictor Coefficients and P-values": sig_text,
            }

            st.markdown(
                """
                <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;
                            padding:1.25rem;height:100%;">
                    <div style="font-size:0.75rem;font-weight:700;color:#6B7280;text-transform:uppercase;
                                letter-spacing:0.05em;margin-bottom:0.75rem;">
                        <i class="fas fa-robot" style="color:#5C45FD;margin-right:0.4rem;"></i>
                        AI Model Interpretation
                    </div>
                """,
                unsafe_allow_html=True,
            )

            interp_key = f"ols_interp_{model_year}_{dep_var}_{model_type}"
            if interp_key not in st.session_state:
                st.session_state[interp_key] = None

            if st.button("✨ Explain This Output", key=f"btn_interp_{interp_key}", type="primary"):
                with st.spinner("Gemini is reading the model output..."):
                    st.session_state[interp_key] = generate_insights(
                        f"OLS Regression Model for {get_variable_label(dep_var)}",
                        interp_context
                    )

            if st.session_state.get(interp_key):
                st.markdown(
                    f"""
                    <div style="font-size:0.85rem;color:#374151;line-height:1.65;margin-top:0.5rem;">
                        {st.session_state[interp_key].replace(chr(10), "<br>")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div style="font-size:0.83rem;color:#9CA3AF;margin-top:0.5rem;font-style:italic;">
                        Click <strong>Explain This Output</strong> above to get a plain-English
                        interpretation of the R², coefficient significance, F-statistic,
                        and model diagnostics — powered by Google Gemini.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)


    # Non-OLS model summary + LLM interpretation (Polynomial, Ridge, LASSO, ElasticNet, RF)
    if res["ols_summary"] is None:
        from utils.llm import generate_insights

        section_header(f"{MODEL_TYPES.get(model_type, model_type)} — Model Summary", icon="file-alt")
        sum_col2, interp_col2 = st.columns([1.1, 0.9])

        with sum_col2:
            cv_text2 = f"{res['cv_r2']:.4f}" if res["cv_r2"] is not None else "N/A"
            # Build a formatted model output card for non-OLS models
            coef_rows = ""
            if hasattr(res["model"], "coef_") and model_type not in ["poly2", "poly3"]:
                for v, c in zip(selected_predictors, res["model"].coef_):
                    coef_rows += f"  {get_variable_label(v):<35} {c:+.6f}\n"
            elif model_type == "random_forest":
                for v, imp in zip(selected_predictors, res["model"].feature_importances_):
                    coef_rows += f"  {get_variable_label(v):<35} importance: {imp:.4f}\n"
            elif model_type in ["poly2", "poly3"]:
                deg = 2 if model_type == "poly2" else 3
                coef_rows += f"  Degree-{deg} polynomial features: {res['p']} total terms\n"
                for c in res["model"].coef_[:8]:
                    coef_rows += f"    coef: {c:+.6f}\n"
                if res["p"] > 8:
                    coef_rows += f"  ... ({res['p'] - 8} more terms)\n"

            summary_text = f"""{MODEL_TYPES.get(model_type, model_type).upper()} RESULTS
{'='*60}
Dep. Variable:    {get_variable_label(dep_var):<30}
Observations:     {res['n']:,}
Predictors:       {res['p']}
Year:             {model_year}
{'='*60}
R-Squared:        {res['r2']:.6f}
Adjusted R²:      {res['adj_r2']:.6f}
RMSE:             {res['rmse']:.6f}
MAE:              {res['mae']:.6f}
Cross-Val R²:     {cv_text2}
{'='*60}
COEFFICIENTS / FEATURE WEIGHTS
{'-'*60}
{coef_rows}{'='*60}
"""
            st.code(summary_text, language=None)

        with interp_col2:
            # Build model-type specific LLM context
            non_ols_context = {
                "Model Type": MODEL_TYPES.get(model_type, model_type),
                "Target Variable": get_variable_label(dep_var),
                "Year": model_year,
                "R-Squared": f"{res['r2']:.4f}",
                "Adjusted R-Squared": f"{res['adj_r2']:.4f}",
                "RMSE": f"{res['rmse']:.4f}",
                "MAE": f"{res['mae']:.4f}",
                "Cross-Validated R²": cv_text2,
                "Observations": f"{res['n']:,}",
                "Predictors Used": ", ".join([get_variable_label(v) for v in selected_predictors]),
            }

            if model_type == "random_forest":
                top3 = sorted(
                    zip([get_variable_label(v) for v in selected_predictors], res["model"].feature_importances_),
                    key=lambda x: x[1], reverse=True
                )[:3]
                non_ols_context["Top 3 Feature Importances"] = ", ".join([f"{k}: {v:.4f}" for k, v in top3])
            elif model_type in ["ridge", "lasso", "elasticnet"]:
                non_ols_context["Regularization"] = model_type.upper()
                if hasattr(res["model"], "coef_"):
                    coef_summary = sorted(
                        zip([get_variable_label(v) for v in selected_predictors], res["model"].coef_),
                        key=lambda x: abs(x[1]), reverse=True
                    )[:4]
                    non_ols_context["Top 4 Coefficients (by magnitude)"] = \
                        ", ".join([f"{k}: {v:+.4f}" for k, v in coef_summary])
            elif model_type in ["poly2", "poly3"]:
                deg = 2 if model_type == "poly2" else 3
                non_ols_context["Polynomial Degree"] = deg
                non_ols_context["Expanded Feature Count"] = res["p"]

            st.markdown(
                """
                <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;
                            padding:1.25rem;">
                    <div style="font-size:0.75rem;font-weight:700;color:#6B7280;text-transform:uppercase;
                                letter-spacing:0.05em;margin-bottom:0.75rem;">
                        <i class="fas fa-robot" style="color:#5C45FD;margin-right:0.4rem;"></i>
                        AI Model Interpretation
                    </div>
                """,
                unsafe_allow_html=True,
            )

            interp_key2 = f"nonols_interp_{model_year}_{dep_var}_{model_type}"
            if interp_key2 not in st.session_state:
                st.session_state[interp_key2] = None

            if st.button("✨ Explain This Output", key=f"btn_interp_{interp_key2}", type="primary"):
                with st.spinner("Gemini is reading the model output..."):
                    st.session_state[interp_key2] = generate_insights(
                        f"{MODEL_TYPES.get(model_type, model_type)} for {get_variable_label(dep_var)}",
                        non_ols_context
                    )

            if st.session_state.get(interp_key2):
                st.markdown(
                    f"""
                    <div style="font-size:0.85rem;color:#374151;line-height:1.65;margin-top:0.5rem;">
                        {st.session_state[interp_key2].replace(chr(10), "<br>")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div style="font-size:0.83rem;color:#9CA3AF;margin-top:0.5rem;font-style:italic;">
                        Click <strong>Explain This Output</strong> above to get a plain-English
                        breakdown of R², RMSE, feature importances or regularization effects
                        — powered by Google Gemini.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

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
