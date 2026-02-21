"""
Theme — McKinsey-grade design system.
Deep navy + electric blue + white. High contrast. Data-forward. Minimal.

Brand references (McKinsey & Company):
  Primary dark:  #051C2C  (Black Pearl)
  Accent blue:   #2251FF  (Blue Ribbon)
  White:         #FFFFFF
  Headlines:     Georgia (serif)   — McKinsey PowerPoint substitute for Bower
  Body:          Inter / Arial     — McKinsey PowerPoint substitute for McKinsey Sans
"""

import streamlit as st

# ── Palette ──────────────────────────────────────────────────────────────────
COLORS = {
    # McKinsey core
    "dark": "#051C2C",
    "blue": "#2251FF",
    "white": "#FFFFFF",
    # Extended neutrals
    "ink": "#0A1628",
    "charcoal": "#1B2A3D",
    "slate": "#3D5168",
    "steel": "#6B7F95",
    "silver": "#A3B1BF",
    "pearl": "#DDE3E9",
    "snow": "#F4F6F8",
    # Semantic accents
    "sapphire": "#2251FF",
    "ruby": "#D63031",
    "emerald": "#00B894",
    "amber": "#FDCB6E",
    "amethyst": "#6C5CE7",
    "topaz": "#E17055",
    # Backward compatibility aliases for dashboard plots
    "teal": "#00B894",      # emerald
    "rose": "#D63031",      # ruby
    "violet": "#6C5CE7",    # amethyst
    "orange": "#E17055",    # topaz
    "cyan": "#74B9FF",      # ocean_light
    # Chart sequence
    "ocean_light": "#74B9FF",
    "navy": "#051C2C",
    "navy_dark": "#030F1A",
}

# ── Plotly template ──────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, Arial, sans-serif", size=13, color=COLORS["slate"]),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    title_font=dict(family="Inter, sans-serif", size=20, color=COLORS["dark"]),
    margin=dict(l=56, r=24, t=64, b=48),
    xaxis=dict(
        gridcolor="#EDF0F4",
        linecolor="#DDE3E9",
        zerolinecolor="#DDE3E9",
        title_font=dict(family="Inter, sans-serif", size=12, color=COLORS["steel"]),
        tickfont=dict(size=11, color=COLORS["steel"]),
    ),
    yaxis=dict(
        gridcolor="#EDF0F4",
        linecolor="#DDE3E9",
        zerolinecolor="#DDE3E9",
        title_font=dict(family="Inter, sans-serif", size=12, color=COLORS["steel"]),
        tickfont=dict(size=11, color=COLORS["steel"]),
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0)",
        font=dict(size=12, color=COLORS["slate"]),
    ),
    hoverlabel=dict(
        bgcolor=COLORS["dark"],
        font_size=13,
        font_family="Inter, sans-serif",
        font_color="#FFFFFF",
        bordercolor=COLORS["dark"],
    ),
    colorway=[
        COLORS["sapphire"], COLORS["ruby"], COLORS["emerald"],
        COLORS["amethyst"], COLORS["topaz"], COLORS["amber"],
        COLORS["ocean_light"],
    ],
)

SEQUENTIAL_COLORS = [
    COLORS["sapphire"], COLORS["ruby"], COLORS["emerald"],
    COLORS["amber"], COLORS["amethyst"], COLORS["topaz"],
    COLORS["ocean_light"],
]


# ── CSS injection ────────────────────────────────────────────────────────────
def inject_tailwind():
    """Inject McKinsey-grade CSS design system."""
    css = """
        <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
              rel="stylesheet">
        <style>
        /* ================================================================== */
        /*  STREAMLIT CHROME                                                  */
        /* ================================================================== */
        #MainMenu, footer, .stDeployButton { display:none !important; }

        html, body, .stApp {
            font-family: 'Inter', Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }
        .block-container {
            padding: 2rem 2.5rem 3rem !important;
            max-width: 1360px !important;
        }

        /* ── Sidebar ────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(160deg, #1A237E 0%, #0D1452 100%) !important;
        }
        [data-testid="stSidebar"], [data-testid="stSidebar"] div, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
            color: rgba(255,255,255,.85) !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {
            color: rgba(255,255,255,.7) !important;
            font-size: .8rem;
            letter-spacing: .02em;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #fff !important;
            font-family: Georgia, serif !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] span,
        [data-testid="stSidebar"] [data-baseweb="select"] div,
        [data-testid="stSidebar"] [data-baseweb="select"] p {
            color: #1a1a1a !important;
        }
        
        /* ── Sidebar Expander Overrides ─────────────────────────────────── */
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background-color: transparent !important;
            border: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary,
        [data-testid="stSidebar"] [data-testid="stExpander"] details {
            background-color: transparent !important;
            border: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
            background-color: rgba(255,255,255,0.05) !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            padding-left: 0.25rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
            display: none !important;
        }

        /* ── Plotly + dataframes ────────────────────────────────────────── */
        .js-plotly-plot { border-radius: 8px; }
        .stDataFrame { border-radius: 8px; overflow: hidden; }

        /* ================================================================== */
        /*  LAYOUT                                                            */
        /* ================================================================== */
        .grid   { display: grid; }
        .grid-cols-2 { grid-template-columns: repeat(2,1fr); }
        .grid-cols-3 { grid-template-columns: repeat(3,1fr); }
        .grid-cols-4 { grid-template-columns: repeat(4,1fr); }
        .flex   { display: flex; }
        .flex-col { flex-direction: column; }
        .items-center { align-items: center; }
        .items-start  { align-items: flex-start; }
        .justify-center { justify-content: center; }
        .justify-between { justify-content: space-between; }
        .gap-2 { gap:.5rem; }   .gap-3 { gap:.75rem; }
        .gap-4 { gap:1rem; }    .gap-5 { gap:1.25rem; }
        .gap-6 { gap:1.5rem; }  .gap-8 { gap:2rem; }
        .space-y-2>div+div { margin-top:.5rem; }
        .space-y-3>div+div { margin-top:.75rem; }

        /* ================================================================== */
        /*  POSITION                                                          */
        /* ================================================================== */
        .relative { position:relative; }
        .absolute { position:absolute; }
        .top-0 { top:0; } .right-0 { right:0; } .bottom-0 { bottom:0; } .left-0 { left:0; }
        .z-10 { z-index:10; }
        .overflow-hidden { overflow:hidden; }

        /* ================================================================== */
        /*  SIZING                                                            */
        /* ================================================================== */
        .h-1  { height:.25rem; } .h-4 { height:1rem; }  .h-6 { height:1.5rem; }
        .h-8  { height:2rem; }   .h-10 { height:2.5rem; } .h-12 { height:3rem; }
        .h-14 { height:3.5rem; } .h-24 { height:6rem; }  .h-32 { height:8rem; }
        .h-64 { height:16rem; }  .h-96 { height:24rem; }
        .w-10 { width:2.5rem; }  .w-12 { width:3rem; }   .w-14 { width:3.5rem; }
        .w-24 { width:6rem; }    .w-32 { width:8rem; }    .w-64 { width:16rem; }
        .w-96 { width:24rem; }   .w-full { width:100%; }
        .max-w-2xl { max-width:42rem; } .max-w-3xl { max-width:48rem; }
        .max-w-4xl { max-width:56rem; }

        /* ================================================================== */
        /*  SPACING                                                           */
        /* ================================================================== */
        .p-3{padding:.75rem} .p-4{padding:1rem} .p-5{padding:1.25rem}
        .p-6{padding:1.5rem} .p-8{padding:2rem} .p-10{padding:2.5rem}
        .px-2{padding-left:.5rem;padding-right:.5rem}
        .px-3{padding-left:.75rem;padding-right:.75rem}
        .px-4{padding-left:1rem;padding-right:1rem}
        .px-5{padding-left:1.25rem;padding-right:1.25rem}
        .px-6{padding-left:1.5rem;padding-right:1.5rem}
        .px-8{padding-left:2rem;padding-right:2rem}
        .px-10{padding-left:2.5rem;padding-right:2.5rem}
        .px-12{padding-left:3rem;padding-right:3rem}
        .py-1{padding-top:.25rem;padding-bottom:.25rem}
        .py-2{padding-top:.5rem;padding-bottom:.5rem}
        .py-3{padding-top:.75rem;padding-bottom:.75rem}
        .py-4{padding-top:1rem;padding-bottom:1rem}
        .py-6{padding-top:1.5rem;padding-bottom:1.5rem}
        .py-8{padding-top:2rem;padding-bottom:2rem}
        .py-10{padding-top:2.5rem;padding-bottom:2.5rem}
        .py-12{padding-top:3rem;padding-bottom:3rem}
        .py-16{padding-top:4rem;padding-bottom:4rem}
        .mb-1{margin-bottom:.25rem}  .mb-2{margin-bottom:.5rem}
        .mb-3{margin-bottom:.75rem}  .mb-4{margin-bottom:1rem}
        .mb-5{margin-bottom:1.25rem} .mb-6{margin-bottom:1.5rem}
        .mb-8{margin-bottom:2rem}    .mb-10{margin-bottom:2.5rem}
        .mt-1{margin-top:.25rem}     .mt-2{margin-top:.5rem}
        .mt-3{margin-top:.75rem}     .mt-4{margin-top:1rem}
        .mt-6{margin-top:1.5rem}     .mt-8{margin-top:2rem}
        .mr-2{margin-right:.5rem}    .mr-3{margin-right:.75rem}
        .mx-auto{margin-left:auto;margin-right:auto}
        .my-3{margin-top:.75rem;margin-bottom:.75rem}

        /* ================================================================== */
        /*  TYPOGRAPHY                                                        */
        /* ================================================================== */
        .font-serif { font-family: Georgia, 'Times New Roman', serif !important; }
        .text-xs{font-size:.75rem;line-height:1rem}
        .text-sm{font-size:.875rem;line-height:1.25rem}
        .text-base{font-size:1rem;line-height:1.5rem}
        .text-lg{font-size:1.125rem;line-height:1.75rem}
        .text-xl{font-size:1.25rem;line-height:1.75rem}
        .text-2xl{font-size:1.5rem;line-height:2rem}
        .text-3xl{font-size:1.875rem;line-height:2.25rem}
        .text-4xl{font-size:2.25rem;line-height:2.5rem}
        .text-5xl{font-size:3rem;line-height:1.15}
        .font-light{font-weight:300}  .font-normal{font-weight:400}
        .font-medium{font-weight:500} .font-semibold{font-weight:600}
        .font-bold{font-weight:700}   .font-extrabold{font-weight:800}
        .font-mono{font-family:ui-monospace,monospace}
        .uppercase{text-transform:uppercase}
        .tracking-tight{letter-spacing:-.025em}
        .tracking-wide{letter-spacing:.025em}
        .tracking-wider{letter-spacing:.05em}
        .leading-tight{line-height:1.25}
        .leading-snug{line-height:1.375}
        .leading-relaxed{line-height:1.625}
        .text-center{text-align:center}
        .text-right{text-align:right}

        /* ================================================================== */
        /*  TEXT COLORS                                                       */
        /* ================================================================== */
        .text-white{color:#fff}
        .text-dark{color:#051C2C}
        .text-blue{color:#2251FF}
        .text-gray-300{color:#D1D5DB} .text-gray-400{color:#9CA3AF}
        .text-gray-500{color:#6B7280} .text-gray-600{color:#4B5563}
        .text-gray-700{color:#374151} .text-gray-800{color:#1F2937}
        .text-slate-400{color:#94A3B8} .text-slate-500{color:#64748B}
        .text-blue-100{color:#DBEAFE} .text-blue-200{color:#BFDBFE}
        .text-blue-400{color:#60A5FA} .text-blue-500{color:#3B82F6}
        .text-blue-600{color:#2563EB} .text-blue-700{color:#1D4ED8}
        .text-blue-800{color:#1E40AF}
        .text-emerald-200{color:#A7F3D0} .text-emerald-600{color:#059669}
        .text-emerald-700{color:#047857} .text-emerald-800{color:#065F46}
        .text-red-200{color:#FECACA} .text-red-500{color:#EF4444}
        .text-red-700{color:#B91C1C} .text-red-800{color:#991B1B}
        .text-amber-500{color:#F59E0B} .text-amber-700{color:#B45309}
        .text-amber-800{color:#92400E}
        .text-purple-600{color:#9333EA} .text-purple-700{color:#7E22CE}
        .text-purple-800{color:#6B21A8}

        /* ================================================================== */
        /*  BACKGROUNDS                                                       */
        /* ================================================================== */
        .bg-white{background:#fff}
        .bg-dark{background:#051C2C}
        .bg-blue{background:#2251FF}
        .bg-gray-50{background:#F9FAFB}  .bg-gray-100{background:#F3F4F6}
        .bg-blue-50{background:#EFF6FF}  .bg-blue-100{background:#DBEAFE}
        .bg-blue-200{background:#BFDBFE}
        .bg-emerald-50{background:#ECFDF5} .bg-emerald-100{background:#D1FAE5}
        .bg-emerald-200{background:#A7F3D0}
        .bg-red-50{background:#FEF2F2}  .bg-red-100{background:#FEE2E2}
        .bg-amber-50{background:#FFFBEB} .bg-amber-100{background:#FEF3C7}
        .bg-purple-50{background:#FAF5FF} .bg-purple-100{background:#F3E8FF}

        /* ================================================================== */
        /*  BORDERS  &  ROUNDING                                              */
        /* ================================================================== */
        .border{border:1px solid #E5E7EB}
        .border-t{border-top:1px solid #E5E7EB}
        .border-b{border-bottom:1px solid #E5E7EB}
        .border-l-4{border-left:4px solid #E5E7EB}
        .border-gray-100{border-color:#F3F4F6} .border-gray-200{border-color:#E5E7EB}
        .border-blue-100{border-color:#DBEAFE}  .border-blue-200{border-color:#BFDBFE}
        .border-blue-500{border-color:#3B82F6}
        .border-emerald-100{border-color:#D1FAE5} .border-emerald-200{border-color:#A7F3D0}
        .border-red-200{border-color:#FECACA}
        .border-amber-200{border-color:#FDE68A}
        .border-transparent{border-color:transparent}
        .rounded{border-radius:.25rem}
        .rounded-lg{border-radius:.5rem}
        .rounded-xl{border-radius:.75rem}
        .rounded-2xl{border-radius:1rem}
        .rounded-3xl{border-radius:1.5rem}
        .rounded-full{border-radius:9999px}

        /* ================================================================== */
        /*  SHADOWS  &  EFFECTS                                               */
        /* ================================================================== */
        .shadow-sm{box-shadow:0 1px 2px rgba(5,28,44,.05)}
        .shadow{box-shadow:0 1px 3px rgba(5,28,44,.08),0 1px 2px rgba(5,28,44,.04)}
        .shadow-md{box-shadow:0 4px 6px -1px rgba(5,28,44,.08),0 2px 4px -2px rgba(5,28,44,.04)}
        .shadow-lg{box-shadow:0 10px 15px -3px rgba(5,28,44,.06),0 4px 6px rgba(5,28,44,.03)}
        .shadow-xl{box-shadow:0 20px 25px -5px rgba(5,28,44,.06),0 8px 10px rgba(5,28,44,.03)}
        .transition-all{transition:all .25s cubic-bezier(.4,0,.2,1)}
        .transition-colors{transition:color .2s,background .2s}
        .opacity-60{opacity:.6} .opacity-80{opacity:.8}

        /* ================================================================== */
        /*  HOVER  (works in Streamlit st.markdown)                           */
        /* ================================================================== */
        .hover-lift:hover { transform:translateY(-3px); box-shadow:0 12px 20px -4px rgba(5,28,44,.1); }
        .hover-lift { transition: transform .25s, box-shadow .25s; }

        /* ================================================================== */
        /*  McKINSEY KPI CARD (the signature element, upgraded)               */
        /* ================================================================== */
        .kpi-card {
            background: #ffffff;
            border: 1px solid rgba(226, 232, 240, 0.8);
            border-radius: 0.75rem;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.25s ease-out;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            text-align: center;
        }
        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
            border-color: rgba(203, 213, 225, 0.9);
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 3px;
        }
        .kpi-card.accent-blue::before   { background: #2251FF; }
        .kpi-card.accent-red::before    { background: #D63031; }
        .kpi-card.accent-green::before  { background: #00B894; }
        .kpi-card.accent-amber::before  { background: #FDCB6E; }
        .kpi-card.accent-purple::before { background: #6C5CE7; }
        .kpi-card.accent-dark::before   { background: #051C2C; }

        .kpi-label {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #64748B;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
        }
        .kpi-value {
            font-family: 'Inter', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
            letter-spacing: -0.02em;
            margin-bottom: 0.4rem;
        }
        .kpi-change {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.15rem 0.5rem;
            border-radius: 9999px;
            margin-top: 0.25rem;
            align-self: center;
        }
        .kpi-change.up   { 
            color: #047857; 
            background: #D1FAE5;
        }
        .kpi-change.down { 
            color: #B91C1C; 
            background: #FEE2E2;
        }

        /* ── Dark variant (for hero) ─────────────────────────────── */
        .kpi-card-dark {
            background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 1rem;
            padding: 1.75rem;
            text-align: center;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .kpi-card-dark:hover { 
            background: linear-gradient(145deg, rgba(255,255,255,0.12), rgba(255,255,255,0.05));
            border-color: rgba(255,255,255,0.25);
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
        }

        /* ================================================================== */
        /*  SECTION HEADER (McKinsey style — clean line)                      */
        /* ================================================================== */
        .section-hdr {
            border-bottom: 2px solid #051C2C;
            padding-bottom: .5rem;
            margin-bottom: 1.25rem;
            margin-top: 2rem;
        }
        .section-hdr h2 {
            font-family: Georgia, serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: #051C2C;
            margin: 0;
        }
        .section-hdr p {
            font-size: .8rem;
            color: #6B7F95;
            margin: .2rem 0 0;
        }

        /* ================================================================== */
        /*  RESPONSIVE                                                        */
        /* ================================================================== */
        @media(max-width:1024px) {
            .grid-cols-4 { grid-template-columns: repeat(2, 1fr); }
            .grid-cols-3 { grid-template-columns: repeat(2, 1fr); }
        }
        @media(max-width:768px){
            .grid-cols-4 { grid-template-columns: repeat(3, 1fr) !important; gap: 0.5rem !important; }
            .grid-cols-2, .grid-cols-3 { grid-template-columns: repeat(2, 1fr) !important; gap: 0.5rem !important; }
            .px-10,.px-12{padding-left:0.75rem;padding-right:0.75rem}
            /* Scale down KPIs severely to fit 3 in a row on mobile */
            .kpi-card { padding: 0.65rem !important; }
            .kpi-value { font-size: 1.15rem !important; }
            .kpi-label { font-size: 0.55rem !important; letter-spacing: 0 !important; margin-bottom: 0.3rem !important; }
            .kpi-label i { margin-right: 0.15rem !important; }
            .kpi-change { font-size: 0.55rem !important; padding: 0.1rem 0.3rem !important; }
            .text-5xl{font-size:1.75rem} .text-4xl{font-size:1.5rem}
        }
        </style>
    """
    if hasattr(st, "html"):
        st.html(css)
    else:
        st.markdown(css, unsafe_allow_html=True)


# ── Reusable header ─────────────────────────────────────────────────────────
def page_header(title: str, subtitle: str = "", icon: str = ""):
    """McKinsey-style page header — serif title, thin rule below."""
    icon_html = (
        f'<i class="fas fa-{icon}" style="color:#2251FF;margin-right:.6rem;font-size:.9em"></i>'
        if icon else ""
    )
    sub = f'<p style="color:#6B7F95;font-size:.9rem;margin:.3rem 0 0">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <style>
        @keyframes bg-pan-left {{
            0% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .header-ribbon {{
            position: relative;
            padding: 1.2rem 1.2rem;
            margin-bottom: 1.5rem;
            background: #0D1452; /* Portfolio deep blue bg */
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        .header-ribbon::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(80deg, #6C5CE7, #38bdf8, #6C5CE7); /* Purple/cyan */
            background-size: 200% 200%;
            animation: bg-pan-left 4s linear infinite;
        }}
        .header-title {{
            font-family: 'Geist', sans-serif !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            margin: 0 !important;
            line-height: 1.3 !important;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.4) !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .header-subtitle {{
            color: #E2E8F0 !important; /* Brighter subtitle */
            font-family: 'Geist Mono', monospace !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            margin: 0.5rem 0 0 0 !important;
            text-shadow: 0 0 10px rgba(226, 232, 240, 0.3) !important;
        }}
        </style>
        <div class="header-ribbon">
            <h1 class="header-title">
                {icon_html}{title}
            </h1>
            <div class="header-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
