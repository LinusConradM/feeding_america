"""
U.S. Food Insecurity Analytics Platform
Conrad Linus Muhirwe — American University
"""
import streamlit as st
import pandas as pd
import warnings

# Suppress expected numpy warnings when calculating aggregations on all-NaN slices
warnings.filterwarnings("ignore", message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", message=".*All-NaN slice encountered.*")

from utils.theme import inject_tailwind





# ── Hero ─────────────────────────────────────────────────────────────────────
hero_html = """
    <div style="background:#051C2C;border-radius:1rem;overflow:hidden;margin-bottom:2rem">
        <div style="padding:3.5rem 3rem 3rem">
            
            <div style="display:flex;gap:.6rem;margin-bottom:1.5rem">
                <span style="background:rgba(34,81,255,.25);color:#74B9FF;font-size:.68rem;
                             font-weight:700;padding:.3rem .85rem;border-radius:9999px;
                             letter-spacing:.06em;text-transform:uppercase">
            </div>

            
            <h1 style="font-family:'Inter',sans-serif;font-size:2.8rem;font-weight:700;
                       color:#FFFFFF;line-height:1.15;margin:0 0 .75rem">
                U.S. Food Insecurity<br>
                <span style="color:#74B9FF">Analytics Platform</span>
            </h1>

            <p style="color:rgba(255,255,255,.55);font-size:1rem;max-width:38rem;
                      line-height:1.65;margin:0 0 2.5rem">
                Investigating patterns, disparities, and socioeconomic drivers of
                food insecurity across 3,100+ U.S. counties over 15 years of data.
            </p>

            
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;max-width:48rem">
                <div class="kpi-card-dark">
                    <div style="font-family:'Inter',sans-serif;font-size:1.75rem;font-weight:700;color:#fff">
                        44.2M</div>
                    <div style="font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;
                                color:rgba(255,255,255,.4);margin-top:.25rem">
                        Americans Affected</div>
                </div>
                <div class="kpi-card-dark">
                    <div style="font-family:'Inter',sans-serif;font-size:1.75rem;font-weight:700;color:#fff">
                        3,100+</div>
                    <div style="font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;
                                color:rgba(255,255,255,.4);margin-top:.25rem">
                        Counties Analyzed</div>
                </div>
                <div class="kpi-card-dark">
                    <div style="font-family:'Inter',sans-serif;font-size:1.75rem;font-weight:700;color:#fff">
                        15</div>
                    <div style="font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;
                                color:rgba(255,255,255,.4);margin-top:.25rem">
                        Years of Data</div>
                </div>
                <div class="kpi-card-dark">
                    <div style="font-family:'Inter',sans-serif;font-size:1.75rem;font-weight:700;color:#fff">
                        47K+</div>
                    <div style="font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;
                                color:rgba(255,255,255,.4);margin-top:.25rem">
                        Observations</div>
                </div>
            </div>
        </div>
    </div>
"""
if hasattr(st, "html"):
    st.html(hero_html)
else:
    st.markdown(hero_html, unsafe_allow_html=True)

# ── Feature cards ────────────────────────────────────────────────────────────
feature_html = """
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-bottom:2.5rem">

        <!-- Executive Overview Card -->
        <div style="background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);
                    border:1px solid rgba(226,232,240,0.8);
                    border-radius:1.25rem;
                    padding:2.5rem;
                    box-shadow:0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -2px rgba(0,0,0,0.03);
                    transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    position:relative;
                    overflow:hidden;" 
             onmouseover="this.style.transform='translateY(-6px)'; this.style.boxShadow='0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04)'; this.style.borderColor='rgba(34,81,255,0.2)';" 
             onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -2px rgba(0,0,0,0.03)'; this.style.borderColor='rgba(226,232,240,0.8)';">
            
            <div style="position:absolute;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg,#2251FF,#74B9FF);"></div>
            
            <div style="width:3rem;height:3rem;background:linear-gradient(135deg,#EFF6FF 0%,#DBEAFE 100%);
                        border-radius:0.75rem;display:flex;align-items:center;justify-content:center;
                        margin-bottom:1.5rem;box-shadow:inset 0 0 0 1px rgba(255,255,255,0.8), 0 2px 4px rgba(34,81,255,0.05);">
                <i class="fas fa-chart-bar" style="color:#2251FF;font-size:1.15rem;"></i>
            </div>
            
            <div style="font-family:'Inter',serif;font-size:1.15rem;font-weight:700;
                        color:#0f172a;margin-bottom:0.75rem;letter-spacing:-0.01em;">Executive Overview</div>
            <p style="color:#64748b;font-size:0.875rem;line-height:1.6;margin:0;">
                National KPIs, trend analysis, regional comparisons, and demographic
                breakdowns at a glance.
            </p>
        </div>

        <!-- Geographic Intelligence Card -->
        <div style="background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);
                    border:1px solid rgba(226,232,240,0.8);
                    border-radius:1.25rem;
                    padding:2.5rem;
                    box-shadow:0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -2px rgba(0,0,0,0.03);
                    transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    position:relative;
                    overflow:hidden;" 
             onmouseover="this.style.transform='translateY(-6px)'; this.style.boxShadow='0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04)'; this.style.borderColor='rgba(0,184,148,0.2)';" 
             onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -2px rgba(0,0,0,0.03)'; this.style.borderColor='rgba(226,232,240,0.8)';">
            
            <div style="position:absolute;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg,#00B894,#55EFC4);"></div>
            
            <div style="width:3rem;height:3rem;background:linear-gradient(135deg,#ECFDF5 0%,#D1FAE5 100%);
                        border-radius:0.75rem;display:flex;align-items:center;justify-content:center;
                        margin-bottom:1.5rem;box-shadow:inset 0 0 0 1px rgba(255,255,255,0.8), 0 2px 4px rgba(0,184,148,0.05);">
                <i class="fas fa-map-marked-alt" style="color:#059669;font-size:1.15rem;"></i>
            </div>
            
            <div style="font-family:'Inter',serif;font-size:1.15rem;font-weight:700;
                        color:#0f172a;margin-bottom:0.75rem;letter-spacing:-0.01em;">Geographic Intelligence</div>
            <p style="color:#64748b;font-size:0.875rem;line-height:1.6;margin:0;">
                Interactive choropleth maps with state-level drill-down, hotspot
                detection, and spatial analysis.
            </p>
        </div>

        <!-- Advanced Analytics Card -->
        <div style="background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);
                    border:1px solid rgba(226,232,240,0.8);
                    border-radius:1.25rem;
                    padding:2.5rem;
                    box-shadow:0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -2px rgba(0,0,0,0.03);
                    transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    position:relative;
                    overflow:hidden;" 
             onmouseover="this.style.transform='translateY(-6px)'; this.style.boxShadow='0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04)'; this.style.borderColor='rgba(108,92,231,0.2)';" 
             onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -2px rgba(0,0,0,0.03)'; this.style.borderColor='rgba(226,232,240,0.8)';">
            
            <div style="position:absolute;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg,#6C5CE7,#A29BFE);"></div>
            
            <div style="width:3rem;height:3rem;background:linear-gradient(135deg,#FAF5FF 0%,#F3E8FF 100%);
                        border-radius:0.75rem;display:flex;align-items:center;justify-content:center;
                        margin-bottom:1.5rem;box-shadow:inset 0 0 0 1px rgba(255,255,255,0.8), 0 2px 4px rgba(108,92,231,0.05);">
                <i class="fas fa-brain" style="color:#7E22CE;font-size:1.15rem;"></i>
            </div>
            
            <div style="font-family:'Inter',serif;font-size:1.15rem;font-weight:700;
                        color:#0f172a;margin-bottom:0.75rem;letter-spacing:-0.01em;">Advanced Analytics</div>
            <p style="color:#64748b;font-size:0.875rem;line-height:1.6;margin:0;">
                Correlation analysis, regression modeling, clustering, and time-series
                exploration tools.
            </p>
        </div>

    </div>
"""
if hasattr(st, "html"):
    st.html(feature_html)
else:
    st.markdown(feature_html, unsafe_allow_html=True)

# ── Data Sources ─────────────────────────────────────────────────────────────
sources_html = """
    <div style="border-bottom:2px solid #051C2C;padding-bottom:.5rem;margin-bottom:1.25rem;margin-top:.5rem">
        <h2 style="font-family:'Inter',sans-serif;font-size:1.15rem;font-weight:700;color:#051C2C;margin:0">
            Data Sources
        </h2>
    </div>

    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1.25rem;margin-bottom:2rem">
        <div style="border:1px solid #DBEAFE;border-left:4px solid #2251FF;
                    border-radius:.5rem;padding:1.25rem 1.5rem">
            <div style="font-size:.7rem;font-weight:700;letter-spacing:.06em;
                        text-transform:uppercase;color:#2251FF;margin-bottom:.35rem">
                Feeding America</div>
            <p style="color:#3D5168;font-size:.85rem;line-height:1.55;margin:0 0 .5rem">
                Map the Meal Gap (2009–2023) — county-level food insecurity estimates,
                cost per meal, budget shortfall, and SNAP participation data.
            </p>
            <span style="background:#EFF6FF;color:#1D4ED8;font-size:.68rem;font-weight:600;
                         padding:.2rem .6rem;border-radius:9999px">Primary Source</span>
        </div>

        <div style="border:1px solid #D1FAE5;border-left:4px solid #00B894;
                    border-radius:.5rem;padding:1.25rem 1.5rem">
            <div style="font-size:.7rem;font-weight:700;letter-spacing:.06em;
                        text-transform:uppercase;color:#00B894;margin-bottom:.35rem">
                U.S. Census Bureau</div>
            <p style="color:#3D5168;font-size:.85rem;line-height:1.55;margin:0 0 .5rem">
                American Community Survey 5-Year Estimates — demographics, income,
                education, and socioeconomic indicators.
            </p>
            <span style="background:#ECFDF5;color:#065F46;font-size:.68rem;font-weight:600;
                         padding:.2rem .6rem;border-radius:9999px">Secondary Source</span>
        </div>
    </div>
"""
if hasattr(st, "html"):
    st.html(sources_html)
else:
    st.markdown(sources_html, unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
footer_html = """
    <div style="border-top:1px solid #E5E7EB;padding-top:1.25rem;margin-top:1.5rem;text-align:center">
        <p style="color:#6B7F95;font-size:.82rem;margin:0">
            Built by <strong style="color:#051C2C">Conrad Linus Muhirwe</strong>
        </p>
        <p style="color:#A3B1BF;font-size:.72rem;margin:.3rem 0 0">
            MS Analytics & AI &middot; American University &middot; 2026
        </p>
    </div>
"""
if hasattr(st, "html"):
    st.html(footer_html)
else:
    st.markdown(footer_html, unsafe_allow_html=True)
