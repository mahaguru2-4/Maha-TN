def get_custom_css() -> str:
    """
    Returns custom CSS for LegalEase Dark Navy + Gold legal-tech theme.
    Deep navy background (#070d1d, #0a1128), gold accents (#d4af37, #f3c68f),
    clean cards, crisp typography, and responsive controls.
    """
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Streamlit App Overrides */
    .stApp {
        background-color: #070d1d !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Main Content Container */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1100px !important;
    }

    /* Top App Header / Branding */
    .legalease-header {
        background: linear-gradient(180deg, #0d152b 0%, #080f21 100%);
        border: 1px solid #1e2c4f;
        border-bottom: 2px solid #d4af37;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .brand-title {
        font-family: 'Cinzel', serif;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #d4af37;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.6);
    }

    .brand-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: #94a3b8;
        letter-spacing: 1px;
        margin-top: 4px;
        text-transform: uppercase;
    }

    /* Card Panels */
    .legal-card {
        background-color: #0d152b;
        border: 1px solid #1e2c4f;
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .legal-card-gold {
        background-color: #0d152b;
        border: 1px solid #d4af37;
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.15);
    }

    .card-title {
        font-family: 'Cinzel', serif;
        font-size: 18px;
        color: #d4af37;
        margin-bottom: 12px;
        font-weight: 600;
    }

    /* Metrics Grid */
    .metric-box {
        background-color: #0d152b;
        border: 1px solid #1e2c4f;
        border-top: 3px solid #d4af37;
        border-radius: 8px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin: 6px 0;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Custom Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #d4af37 0%, #aa8528 100%) !important;
        color: #070d1d !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.25) !important;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #f3c68f 0%, #d4af37 100%) !important;
        color: #070d1d !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(212, 175, 55, 0.4) !important;
    }

    /* Secondary / Download Buttons */
    div.stDownloadButton > button:first-child {
        background-color: #121c38 !important;
        color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.1rem !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stDownloadButton > button:first-child:hover {
        background-color: #d4af37 !important;
        color: #070d1d !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3) !important;
    }

    /* Form Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background-color: #0d152b !important;
        color: #f8fafc !important;
        border: 1px solid #233257 !important;
        border-radius: 6px !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 8px rgba(212, 175, 55, 0.3) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #1e2c4f;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: #0d152b;
        border-radius: 6px 6px 0px 0px;
        color: #94a3b8;
        font-size: 14px;
        font-weight: 500;
        border: 1px solid transparent;
        border-bottom: none;
        padding: 0 18px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #131e3d !important;
        color: #d4af37 !important;
        border: 1px solid #233257 !important;
        border-bottom: 2px solid #d4af37 !important;
        font-weight: 600 !important;
    }

    /* Legal Disclaimer Banner */
    .disclaimer-banner {
        background-color: #0a1124;
        border-left: 4px solid #d4af37;
        border-radius: 4px;
        padding: 12px 18px;
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.5;
        margin-top: 24px;
    }

    /* Auth Box */
    .auth-container {
        max-width: 460px;
        margin: 40px auto;
        background-color: #0d152b;
        border: 1px solid #233257;
        border-top: 3px solid #d4af37;
        border-radius: 12px;
        padding: 36px 32px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        text-align: center;
    }

    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
