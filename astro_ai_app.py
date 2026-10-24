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

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    
    .block-container {
        padding: 1rem 1rem 2rem 1rem !important;
    }
    
    .main-header {
        font-size: 1.9rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7c3aed 0%, #2563eb 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.15rem;
        line-height: 1.2;
    }
    
    .sub-header {
        text-align: center;
        color: #64748b;
        font-size: 0.88rem;
        margin-bottom: 1.1rem;
    }
    
    .planet-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        padding: 0.85rem 0.5rem;
        border-radius: 14px;
        color: white;
        text-align: center;
        margin-bottom: 0.55rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
    }
    
    .planet-name { font-size: 0.92rem; font-weight: 700; color: #a5b4fc; margin-bottom: 0.25rem; }
    .planet-sign { font-size: 1.1rem; font-weight: 600; margin: 0.15rem 0; }
    .planet-degree { font-size: 0.82rem; color: #94a3b8; }
    .planet-nak { font-size: 0.72rem; color: #64748b; margin-top: 0.2rem; }
    
    .signal-card {
        padding: 1.15rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin: 0.7rem 0;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    }
    
    .signal-bullish { background: linear-gradient(135deg, #059669 0%, #10b981 100%); }
    .signal-bearish { background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); }
    .signal-neutral { background: linear-gradient(135deg, #475569 0%, #64748b 100%); }
    
    .day-bullish { background: #064e3b; border-left: 4px solid #10b981; padding: 0.6rem 0.8rem; border-radius: 8px; margin: 0.3rem 0; }
    .day-bearish { background: #7f1d1d; border-left: 4px solid #ef4444; padding: 0.6rem 0.8rem; border-radius: 8px; margin: 0.3rem 0; }
    .day-neutral { background: #1e293b; border-left: 4px solid #64748b; padding: 0.6rem 0.8rem; border-radius: 8px; margin: 0.3rem 0; }
    
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 10px 14px;
        border-radius: 12px;
    }
    
    div[data-testid="stMetric"] label { color: #94a3b8 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 1.25rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 5px; overflow-x: auto; }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: nowrap;
        background-color: #1e293b;
        border-radius: 10px;
        color: #94a3b8;
        padding: 0 12px;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
        color: white !important;
    }
    
    .stApp { background: #0f172a; }
    h1, h2, h3, h4, p, span, label { color: #e2e8f0 !important; }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #a5b4fc !important;
        margin: 0.9rem 0 0.5rem 0;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid #334155;
    }
    
    .retro-badge {
        background: #7f1d1d;
        color: #fecaca;
        padding: 0.35rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.3rem 0;
    }
    
    .direct-badge {
        background: #064e3b;
        color: #a7f3d0;
        padding: 0.35rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA ====================

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
    "Mesh ♈", "Vrishabh ♉", "Mithun ♊", "Kark ♋",
    "Simha ♌", "Kanya ♍", "Tula ♎", "Vrishchik ♏",
    "Dhanu ♐", "Makar ♑", "Kumbh ♒", "Meen ♓"
]

SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
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

def get_planet_data(jd, planet_id):
    result, ret = swe.calc_ut(jd, planet_id)
    lon = result[0]
    speed = result[3]
    return lon, speed

def longitude_to_sign(lon):
    sign_num = int(lon // 30) % 12
    degree = lon % 30
    return SIGNS[sign_num], SIGNS_EN[sign_num], degree, sign_num

def get_nakshatra(lon):
    nak_num = int((lon % 360) / (360 / 27)) % 27
    pada = int(((lon % 360) % (360 / 27)) / (360 / 108)) + 1
    return NAKSHATRAS[nak_num], pada

def calculate_planets(date_time):
    jd = get_julian_day(date_time)
    positions = {}
    
    for name, planet_id in PLANETS.items():
        lon, speed = get_planet_data(jd, planet_id)
        
        if name == "Rahu":
            ketu_lon = (lon + 180) % 360
            sign_hi, sign_en, deg, _ = longitude_to_sign(ketu_lon)
            nak, pada = get_nakshatra(ketu_lon)
            positions["Ketu"] = {
                "longitude": ketu_lon, "sign": sign_hi, "sign_en": sign_en,
                "degree": deg, "nakshatra": nak, "pada": pada, "speed": 0, "retro": False
            }
        
        sign_hi, sign_en, deg, _ = longitude_to_sign(lon)
        nak, pada = get_nakshatra(lon)
        is_retro = speed < 0 if name not in ["Sun", "Moon", "Rahu"] else False
        
        positions[name] = {
            "longitude": lon, "sign": sign_hi, "sign_en": sign_en,
            "degree": deg, "nakshatra": nak, "pada": pada,
            "speed": speed, "retro": is_retro
        }
    
    return positions

def get_major_aspects(positions):
    aspects = []
    planet_list = [p for p in positions.keys() if p != "Ketu"]
    
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
                        "planet1": p1, "planet2": p2,
                        "aspect": name, "orb": round(abs(diff - angle), 1)
                    })
    return aspects

def get_astro_signal(positions, aspects):
    score = 0
    reasons = []
    
    moon_sign = positions["Moon"]["sign_en"]
    if moon_sign in ["Cancer", "Taurus", "Pisces", "Leo", "Sagittarius"]:
        score += 1
        reasons.append("Moon supportive sign mein hai (positive mood)")
    elif moon_sign in ["Scorpio", "Capricorn", "Aquarius", "Virgo"]:
        score -= 1
        reasons.append("Moon challenging sign mein hai")
    
    if positions["Mercury"]["retro"]:
        score -= 2
        reasons.append("⚠️ Mercury Retrograde chal raha hai (confusion / delays)")
    
    for asp in aspects:
        planets = [asp["planet1"], asp["planet2"]]
        if "Jupiter" in planets:
            if "Trine" in asp["aspect"] or "Sextile" in asp["aspect"]:
                score += 2
                reasons.append(f"Jupiter {asp['aspect']} → Expansion positive")
            elif "Square" in asp["aspect"] or "Opposition" in asp["aspect"]:
                score -= 1
                reasons.append(f"Jupiter {asp['aspect']} → Caution")
        
        if "Saturn" in planets:
            if "Square" in asp["aspect"] or "Opposition" in asp["aspect"]:
                score -= 2
                reasons.append(f"Saturn {asp['aspect']} → Pressure / Restriction")
            elif "Trine" in asp["aspect"]:
                score += 1
                reasons.append(f"Saturn {asp['aspect']} → Disciplined growth")
        
        if "Mars" in planets and ("Square" in asp["aspect"] or "Opposition" in asp["aspect"]):
            score -= 1
            reasons.append(f"Mars {asp['aspect']} → Volatility possible")
    
    if not positions["Venus"]["retro"]:
        score += 0.5
    
    if score >= 2.5:
        return "BULLISH", "🟢", round(score, 1), reasons
    elif score <= -2:
        return "BEARISH", "🔴", round(score, 1), reasons
    else:
        return "NEUTRAL", "🟡", round(score, 1), reasons

def get_upcoming_bias(days=10):
    results = []
    base = datetime.now()
    
    for i in range(days):
        dt = base + timedelta(days=i)
        dt_utc = dt - timedelta(hours=5, minutes=30)
        pos = calculate_planets(dt_utc)
        asp = get_major_aspects(pos)
        signal, emoji, score, _ = get_astro_signal(pos, asp)
        
        results.append({
            "date": dt.strftime("%d %b %Y"),
            "day": dt.strftime("%A"),
            "signal": signal,
            "emoji": emoji,
            "score": score,
            "mercury_retro": pos["Mercury"]["retro"]
        })
    
    return results

def get_birth_analysis(dob):
    dt = datetime.combine(dob, datetime.min.time()) + timedelta(hours=12)
    pos = calculate_planets(dt)
    
    moon_sign = pos["Moon"]["sign"]
    sun_sign = pos["Sun"]["sign"]
    moon_nak = pos["Moon"]["nakshatra"]
    
    analysis = []
    analysis.append(f"**Janma Rashi (Moon Sign):** {moon_sign}")
    analysis.append(f"**Surya Rashi:** {sun_sign}")
    analysis.append(f"**Janma Nakshatra:** {moon_nak} (Pada {pos['Moon']['pada']})")
    
    moon_en = pos["Moon"]["sign_en"]
    if moon_en in ["Cancer", "Pisces", "Scorpio"]:
        analysis.append("Swabhav: Emotional & Intuitive trader ho sakte ho")
    elif moon_en in ["Aries", "Leo", "Sagittarius"]:
        analysis.append("Swabhav: Aggressive & Risk-taking tendency")
    elif moon_en in ["Taurus", "Virgo", "Capricorn"]:
        analysis.append("Swabhav: Practical & Patient approach better rehta hai")
    else:
        analysis.append("Swabhav: Balanced & Analytical approach suitable")
    
    return analysis, pos

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
    st.markdown('<p class="sub-header">Share Bazaar • Financial Astrology • हिंदी</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        selected_date = st.date_input("📅 Date", datetime.now().date())
        selected_time = st.time_input("🕐 Time (IST)", datetime.now().time())
        
        dt = datetime.combine(selected_date, selected_time)
        dt_utc = dt - timedelta(hours=5, minutes=30)
        
        st.divider()
        st.markdown("### 🎂 Janam Kundali")
        dob = st.date_input("Apni Date of Birth", value=datetime(1995, 1, 1).date())
        
        st.divider()
        
        market_option = st.selectbox(
            "📊 Market",
            ["Nifty 50", "Bank Nifty", "Finnifty", "Sensex", "Reliance", "TCS", "HDFC Bank", "Gold", "Custom"]
        )
        
        symbol_map = {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK",
            "Finnifty": "NIFTY_FIN_SERVICE.NS",
            "Sensex": "^BSESN",
            "Reliance": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "HDFC Bank": "HDFCBANK.NS",
            "Gold": "GC=F"
        }
        
        if market_option == "Custom":
            symbol = st.text_input("Symbol", "INFY.NS")
        else:
            symbol = symbol_map.get(market_option, "^NSEI")
        
        period = st.selectbox("Chart Period", ["1mo", "3mo", "6mo", "1y"], index=1)
        
        st.divider()
        st.caption("⚠️ Sirf educational purpose ke liye. Financial advice nahi hai.")
    
    positions = calculate_planets(dt_utc)
    aspects = get_major_aspects(positions)
    signal, emoji, score, reasons = get_astro_signal(positions, aspects)
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Date", selected_date.strftime("%d %b %Y"))
    with m2:
        st.metric("Moon", positions["Moon"]["sign"])
    
    m3, m4 = st.columns(2)
    with m3:
        st.metric("Astro Signal", f"{emoji} {signal}")
    with m4:
        st.metric("Score", f"{score:+}")
    
    if positions["Mercury"]["retro"]:
        st.markdown('<div class="retro-badge">⚠️ Mercury RETROGRADE chal raha hai</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="direct-badge">✅ Mercury Direct hai</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🪐 Planets", "📅 Timing", "📊 Chart", "🎂 Kundali", "ℹ️ Info"
    ])
    
    with tab1:
        st.markdown('<p class="section-title">Graha Sthiti (Planetary Positions)</p>', unsafe_allow_html=True)
        
        planet_order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]
        cols = st.columns(3)
        
        for idx, planet in enumerate(planet_order):
            if planet in positions:
                pos = positions[planet]
                retro_tag = " ℞" if pos.get("retro") else ""
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="planet-card">
                        <div class="planet-name">{planet}{retro_tag}</div>
                        <div class="planet-sign">{pos['sign']}</div>
                        <div class="planet-degree">{pos['degree']:.1f}°</div>
                        <div class="planet-nak">{pos['nakshatra']} (P{pos['pada']})</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        if aspects:
            st.markdown('<p class="section-title">Mukhya Drishti (Major Aspects)</p>', unsafe_allow_html=True)
            for asp in aspects[:8]:
                st.markdown(f"**{asp['planet1']}** {asp['aspect']} **{asp['planet2']}**  \n`Orb: {asp['orb']}°`")
    
    with tab2:
        st.markdown('<p class="section-title">Aane Wale Dinon Ka Astro Timing</p>', unsafe_allow_html=True)
        st.caption("Agle 10 din ka Bullish / Bearish / Neutral outlook")
        
        upcoming = get_upcoming_bias(10)
        
        for day in upcoming:
            css_class = {
                "BULLISH": "day-bullish",
                "BEARISH": "day-bearish",
                "NEUTRAL": "day-neutral"
            }[day["signal"]]
            
            retro_text = " | ⚠️ Merc Retro" if day["mercury_retro"] else ""
            
            st.markdown(f"""
            <div class="{css_class}">
                <b>{day['date']}</b> ({day['day']}) — {day['emoji']} <b>{day['signal']}</b>
                &nbsp;&nbsp; Score: {day['score']:+}{retro_text}
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("**Summary:**")
        bull = sum(1 for d in upcoming if d["signal"] == "BULLISH")
        bear = sum(1 for d in upcoming if d["signal"] == "BEARISH")
        neut = sum(1 for d in upcoming if d["signal"] == "NEUTRAL")
        st.write(f"🟢 Bullish din: **{bull}** | 🔴 Bearish din: **{bear}** | 🟡 Neutral din: **{neut}**")
    
    with tab3:
        st.markdown(f'<p class="section-title">{market_option} Chart</p>', unsafe_allow_html=True)
        
        with st.spinner("Market data load ho raha hai..."):
            df = get_market_data(symbol, period)
        
        if df is not None and not df.empty:
            current = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2] if len(df) > 1 else current
            change = current - prev
            pct = (change / prev) * 100
            
            c1, c2 = st.columns(2)
            c1.metric("Price", f"₹{current:,.1f}", f"{change:+.1f} ({pct:+.2f}%)")
            c2.metric("Volume", f"{df['Volume'].iloc[-1]/1e6:.1f}M")
            
            fig = create_candlestick(df, market_option)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            rets = df['Close'].pct_change().dropna()
            s1, s2 = st.columns(2)
            s1.metric("Period Return", f"{((current/df['Close'].iloc[0])-1)*100:.1f}%")
            s2.metric("Volatility", f"{rets.std()*100:.1f}%")
        else:
            st.error("Data load nahi hua. Symbol check karein.")
    
    with tab4:
        st.markdown('<p class="section-title">Aapki Janam Kundali (Basic)</p>', unsafe_allow_html=True)
        
        analysis, birth_pos = get_birth_analysis(dob)
        
        for line in analysis:
            st.markdown(f"- {line}")
        
        st.divider()
        st.markdown("**Janam ke samay ke mukhya Grah:**")
        
        cols = st.columns(3)
        for idx, planet in enumerate(["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter"]):
            if planet in birth_pos:
                pos = birth_pos[planet]
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="planet-card">
                        <div class="planet-name">{planet}</div>
                        <div class="planet-sign">{pos['sign']}</div>
                        <div class="planet-nak">{pos['nakshatra']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.info("Yeh basic analysis hai. Poori kundali ke liye exact birth time aur place chahiye.")
    
    with tab5:
        st.markdown('<p class="section-title">App ke baare mein</p>', unsafe_allow_html=True)
        
        st.markdown("""
        Yeh **Astro AI** prototype hai jisme:
        
        - Graha sthiti aur Nakshatra
        - Mercury Retrograde dete
