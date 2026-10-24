import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import swisseph as swe

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Astro AI - Share Bazaar",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CUSTOM CSS (Mobile Optimized) ====================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .main-header {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7c3aed 0%, #2563eb 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    
    .sub-header {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }
    
    .planet-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        padding: 0.9rem 0.6rem;
        border-radius: 14px;
        color: white;
        text-align: center;
        margin-bottom: 0.6rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
    }
    
    .planet-name {
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        color: #a5b4fc;
    }
    
    .planet-sign {
        font-size: 1.15rem;
        font-weight: 600;
        margin: 0.2rem 0;
    }
    
    .planet-degree {
        font-size: 0.85rem;
        color: #94a3b8;
    }
    
    .planet-nak {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    .signal-card {
        padding: 1.2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin: 0.8rem 0;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    }
    
    .signal-bullish {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    }
    
    .signal-bearish {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    }
    
    .signal-neutral {
        background: linear-gradient(135deg, #475569 0%, #64748b 100%);
    }
    
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 12px 16px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 1.3rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        overflow-x: auto;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: nowrap;
        background-color: #1e293b;
        border-radius: 10px;
        color: #94a3b8;
        padding: 0 14px;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
        color: white !important;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3rem;
        font-weight: 600;
        background: linear-gradient(90deg, #7c3aed, #2563eb);
        color: white;
        border: none;
    }
    
    section[data-testid="stSidebar"] {
        background: #0f172a;
    }
    
    .stApp {
        background: #0f172a;
    }
    
    h1, h2, h3, h4, p, span, label {
        color: #e2e8f0 !important;
    }
    
    .stAlert {
        border-radius: 12px;
    }
    
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #a5b4fc !important;
        margin: 1rem 0 0.6rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ASTROLOGY DATA ====================

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
}

SIGNS = [
    "Aries ♈", "Taurus ♉", "Gemini ♊", "Cancer ♋",
    "Leo ♌", "Virgo ♍", "Libra ♎", "Scorpio ♏",
    "Sagittarius ♐", "Capricorn ♑", "Aquarius ♒", "Pisces ♓"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# ==================== FUNCTIONS ====================

def get_julian_day(dt):
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

def get_planet_position(jd, planet_id):
    result, _ = swe.calc_ut(jd, planet_id)
    return result[0]

def longitude_to_sign(lon):
    sign_num = int(lon // 30)
    degree = lon % 30
    return SIGNS[sign_num], degree, sign_num

def get_nakshatra(lon):
    nak_num = int((lon % 360) / (360 / 27))
    pada = int(((lon % 360) % (360 / 27)) / (360 / 108)) + 1
    return NAKSHATRAS[nak_num], pada

def calculate_planets(date_time):
    jd = get_julian_day(date_time)
    positions = {}
    
    for name, planet_id in PLANETS.items():
        lon = get_planet_position(jd, planet_id)
        
        if name == "Rahu":
            ketu_lon = (lon + 180) % 360
            sign, deg, _ = longitude_to_sign(ketu_lon)
            nak, pada = get_nakshatra(ketu_lon)
            positions["Ketu"] = {
                "longitude": ketu_lon,
                "sign": sign,
                "degree": deg,
                "nakshatra": nak,
                "pada": pada
            }
        
        sign, deg, _ = longitude_to_sign(lon)
        nak, pada = get_nakshatra(lon)
        positions[name] = {
            "longitude": lon,
            "sign": sign,
            "degree": deg,
            "nakshatra": nak,
            "pada": pada
        }
    
    return positions

def get_major_aspects(positions):
    aspects = []
    planet_list = list(positions.keys())
    
    aspect_types = {
        0: ("Conjunction ☌", 8),
        60: ("Sextile ⚹", 5),
        90: ("Square □", 7),
        120: ("Trine △", 7),
        180: ("Opposition ☍", 8)
    }
    
    for i, p1 in enumerate(planet_list):
        for p2 in planet_list[i+1:]:
            lon1 = positions[p1]["longitude"]
            lon2 = positions[p2]["longitude"]
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff
            
            for angle, (name, orb) in aspect_types.items():
                if abs(diff - angle) <= orb:
                    aspects.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": name,
                        "orb": round(abs(diff - angle), 1)
                    })
    return aspects

def get_astro_signal(positions, aspects):
    score = 0
    reasons = []
    
    moon_sign = positions["Moon"]["sign"]
    if any(x in moon_sign for x in ["Cancer", "Taurus", "Pisces", "Leo"]):
        score += 1
        reasons.append("Moon supportive sign mein hai")
    elif any(x in moon_sign for x in ["Scorpio", "Capricorn", "Aquarius"]):
        score -= 1
        reasons.append("Moon challenging sign mein hai")
    
    for asp in aspects:
        planets = [asp["planet1"], asp["planet2"]]
        if "Jupiter" in planets:
            if "Trine" in asp["aspect"] or "Sextile" in asp["aspect"]:
                score += 2
                reasons.append(f"Jupiter {asp['aspect']} → Positive expansion")
            elif "Square" in asp["aspect"] or "Opposition" in asp["aspect"]:
                score -= 1
                reasons.append(f"Jupiter {asp['aspect']} → Caution needed")
        
        if "Saturn" in planets:
            if "Square" in asp["aspect"] or "Opposition" in asp["aspect"]:
                score -= 2
                reasons.append(f"Saturn {asp['aspect']} → Pressure / Restriction")
            elif "Trine" in asp["aspect"]:
                score += 1
                reasons.append(f"Saturn {asp['aspect']} → Disciplined growth")
    
    if score >= 2:
        return "BULLISH", "🟢", score, reasons
    elif score <= -2:
        return "BEARISH", "🔴", score, reasons
    else:
        return "NEUTRAL", "🟡", score, reasons

@st.cache_data(ttl=300)
def get_market_data(symbol, period="3mo"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df
    except:
        return None

def create_candlestick(df, title):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#e2e8f0")),
        yaxis_title="Price (₹)",
        template="plotly_dark",
        height=340,
        margin=dict(l=10, r=10, t=40, b=20),
        xaxis_rangeslider_visible=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.8)",
        font=dict(color="#94a3b8"),
        xaxis=dict(gridcolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b")
    )
    return fig

# ==================== MAIN APP ====================

def main():
    st.markdown('<h1 class="main-header">🪐 Astro AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Share Bazaar • Financial Astrology</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        selected_date = st.date_input("📅 Date", datetime.now().date())
        selected_time = st.time_input("🕐 Time (IST)", datetime.now().time())
        
        dt = datetime.combine(selected_date, selected_time)
        dt_utc = dt - timedelta(hours=5, minutes=30)
        
        st.divider()
        
        market_option = st.selectbox(
            "📊 Market",
            ["Nifty 50", "Bank Nifty", "Sensex", "Reliance", "TCS", "HDFC Bank", "Custom"]
        )
        
        symbol_map = {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK",
            "Sensex": "^BSESN",
            "Reliance": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "HDFC Bank": "HDFCBANK.NS"
        }
        
        if market_option == "Custom":
            symbol = st.text_input("Symbol", "INFY.NS")
        else:
            symbol = symbol_map[market_option]
        
        period = st.selectbox("Chart Period", ["1mo", "3mo", "6mo", "1y"], index=1)
        
        st.divider()
        st.caption("⚠️ Educational purpose only. Not financial advice.")
    
    positions = calculate_planets(dt_utc)
    aspects = get_major_aspects(positions)
    signal, emoji, score, reasons = get_astro_signal(positions, aspects)
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Date", selected_date.strftime("%d %b %Y"))
    with m2:
        st.metric("Moon", positions["Moon"]["sign"].split()[0])
    
    m3, m4 = st.columns(2)
    with m3:
        st.metric("Astro Signal", f"{emoji} {signal}")
    with m4:
        st.metric("Score", f"{score:+d}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🪐 Planets", "📊 Chart", "🔮 Analysis", "ℹ️ Info"])
    
    with tab1:
        st.markdown('<p class="section-title">Planetary Positions</p>', unsafe_allow_html=True)
        
        planet_order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]
        cols = st.columns(3)
        
        for idx, planet in enumerate(planet_order):
            if planet in positions:
                pos = positions[planet]
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="planet-card">
                        <div class="planet-name">{planet}</div>
                        <div class="planet-sign">{pos['sign']}</div>
                        <div class="planet-degree">{pos['degree']:.1f}°</div>
                        <div class="planet-nak">{pos['nakshatra']} (P{pos['pada']})</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        if aspects:
            st.markdown('<p class="section-title">Major Aspects</p>', unsafe_allow_html=True)
            for asp in aspects[:8]:
                st.markdown(f"**{asp['planet1']}** {asp['aspect']} **{asp['planet2']}**  \n`Orb: {asp['orb']}°`")
    
    with tab2:
        st.markdown(f'<p class="section-title">{market_option}</p>', unsafe_allow_html=True)
        
        with st.spinner("Loading market data..."):
            df = get_market_data(symbol, period)
        
        if df is not None and not df.empty:
            current = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2] if len(df) > 1 else current
            change = current - prev
            pct = (change / prev) * 100
            
            c1, c2 = st.columns(2)
            c1.metric("Price", f"₹{current:,.1f}", f"{change:+.1f} ({pct:+.2f}%)")
            c2.metric("Volume", f"{df['Volume'].iloc[-1]/1e6:.1f}M")
            
            fig = create_candlestick(df, f"{market_option}")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            rets = df['Close'].pct_change().dropna()
            s1, s2 = st.columns(2)
            s1.metric("Period Return", f"{((current/df['Close'].iloc[0])-1)*100:.1f}%")
            s2.metric("Volatility", f"{rets.std()*100:.1f}%")
        else:
            st.error("Data load nahi hua. Symbol check karein.")
    
    with tab3:
        st.markdown('<p class="section-title">Astro Market Bias</p>', unsafe_allow_html=True)
        
        signal_class = {
            "BULLISH": "signal-bullish",
            "BEARISH": "signal-bearish",
            "NEUTRAL": "signal-neutral"
        }[signal]
        
        st.markdown(f"""
        <div class="signal-card {signal_class}">
            <div style="font-size:2rem;">{emoji}</div>
            <div style="font-size:1.5rem; font-weight:700; margin:0.3rem 0;">{signal}</div>
            <div style="opacity:0.9;">Score: {score:+d}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if reasons:
            st.markdown("**Reasons:**")
            for r in reasons:
                st.markdown(f"• {r}")
        else:
            st.info("Koi strong aspect nahi dikha.")
        
        st.divider()
        
        st.markdown('<p class="section-title">Key Planets</p>', unsafe_allow_html=True)
        
        moon = positions["Moon"]
        jup = positions["Jupiter"]
        sat = positions["Saturn"]
        
        st.markdown(f"""
        **Moon** → {moon['sign']} ({moon['degree']:.1f}°)  
        Nakshatra: {moon['nakshatra']} Pada {moon['pada']}  
        *Short-term market mood*
        
        **Jupiter** → {jup['sign']} ({jup['degree']:.1f}°)  
        *Expansion & optimism*
        
        **Saturn** → {sat['sign']} ({sat['degree']:.1f}°)  
        *Discipline & restriction*
        
        **Rahu-Ketu** → {positions['Rahu']['sign']} / {positions['Ketu']['sign']}  
        *Turning points axis*
        """)
        
        st.warning("Yeh analysis educational hai. Trading decision apni zimmedari par lein.")
    
    with tab4:
        st.markdown('<p class="section-title">About This App</p>', unsafe_allow_html=True)
        
        st.markdown("""
        Yeh **Astro AI** prototype hai jo:
        
        - Planetary positions calculate karta hai
        - Major aspects dhundhta hai
        - Simple market bias generate karta hai
        - Live stock/index charts dikhata hai
        
        ### Technology
        - Swiss Ephemeris
        - Yahoo Finance
        - Streamlit + Plotly
        
        ### Future Ideas
        - Birth chart integration
        - Mercury retrograde detection
        - Historical backtesting
        - AI Chat analysis
        - Telegram alerts
        
        ---
        **Made for learning** | Not financial advice
        """)

if __name__ == "__main__":
    main()
