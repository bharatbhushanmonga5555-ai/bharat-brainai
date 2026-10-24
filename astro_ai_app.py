import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import swisseph as swe

st.set_page_config(page_title="Astro AI", page_icon="🪐", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding: 1rem !important;}
.main-header {font-size: 1.8rem; font-weight: 800; text-align: center; color: #a78bfa; margin-bottom: 0.2rem;}
.sub-header {text-align: center; color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;}
.planet-card {background: #1e293b; border: 1px solid #334155; padding: 0.8rem 0.4rem; border-radius: 12px; text-align: center; margin-bottom: 0.5rem;}
.day-bullish {background: #064e3b; border-left: 4px solid #10b981; padding: 0.55rem 0.7rem; border-radius: 8px; margin: 0.25rem 0;}
.day-bearish {background: #7f1d1d; border-left: 4px solid #ef4444; padding: 0.55rem 0.7rem; border-radius: 8px; margin: 0.25rem 0;}
.day-neutral {background: #1e293b; border-left: 4px solid #64748b; padding: 0.55rem 0.7rem; border-radius: 8px; margin: 0.25rem 0;}
.retro-badge {background: #7f1d1d; color: #fecaca; padding: 0.3rem 0.6rem; border-radius: 20px; font-size: 0.8rem; display: inline-block;}
.direct-badge {background: #064e3b; color: #a7f3d0; padding: 0.3rem 0.6rem; border-radius: 20px; font-size: 0.8rem; display: inline-block;}
div[data-testid="stMetric"] {background: #1e293b; border: 1px solid #334155; padding: 10px; border-radius: 10px;}
.stApp {background: #0f172a;}
h1,h2,h3,p,span,label {color: #e2e8f0 !important;}
</style>
""", unsafe_allow_html=True)

PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
           "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Rahu": swe.TRUE_NODE}

SIGNS = ["Mesh ♈", "Vrishabh ♉", "Mithun ♊", "Kark ♋", "Simha ♌", "Kanya ♍",
         "Tula ♎", "Vrishchik ♏", "Dhanu ♐", "Makar ♑", "Kumbh ♒", "Meen ♓"]

SIGNS_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
              "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
              "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
              "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

def get_jd(dt):
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60)

def get_planet_data(jd, pid):
    res, _ = swe.calc_ut(jd, pid)
    return res[0], res[3]

def lon_to_sign(lon):
    n = int(lon // 30) % 12
    return SIGNS[n], SIGNS_EN[n], lon % 30

def get_nak(lon):
    n = int((lon % 360) / (360/27)) % 27
    p = int(((lon % 360) % (360/27)) / (360/108)) + 1
    return NAKSHATRAS[n], p

def calc_planets(dt):
    jd = get_jd(dt)
    pos = {}
    for name, pid in PLANETS.items():
        lon, speed = get_planet_data(jd, pid)
        if name == "Rahu":
            klon = (lon + 180) % 360
            s, se, d = lon_to_sign(klon)
            nak, pada = get_nak(klon)
            pos["Ketu"] = {"sign": s, "sign_en": se, "degree": d, "nakshatra": nak, "pada": pada, "retro": False}
        s, se, d = lon_to_sign(lon)
        nak, pada = get_nak(lon)
        retro = speed < 0 if name not in ["Sun", "Moon", "Rahu"] else False
        pos[name] = {"sign": s, "sign_en": se, "degree": d, "nakshatra": nak, "pada": pada, "retro": retro, "lon": lon}
    return pos

def get_aspects(pos):
    aspects = []
    plist = [p for p in pos if p != "Ketu"]
    types = {0: ("Conjunction", 8), 60: ("Sextile", 5), 90: ("Square", 7), 120: ("Trine", 7), 180: ("Opposition", 8)}
    for i, p1 in enumerate(plist):
        for p2 in plist[i+1:]:
            diff = abs(pos[p1]["lon"] - pos[p2]["lon"]) % 360
            if diff > 180: diff = 360 - diff
            for ang, (name, orb) in types.items():
                if abs(diff - ang) <= orb:
                    aspects.append({"p1": p1, "p2": p2, "asp": name, "orb": round(abs(diff-ang), 1)})
    return aspects

def get_signal(pos, aspects):
    score = 0
    reasons = []
    ms = pos["Moon"]["sign_en"]
    if ms in ["Cancer", "Taurus", "Pisces", "Leo", "Sagittarius"]:
        score += 1
        reasons.append("Moon supportive sign mein hai")
    elif ms in ["Scorpio", "Capricorn", "Aquarius", "Virgo"]:
        score -= 1
        reasons.append("Moon challenging sign mein hai")
    if pos["Mercury"]["retro"]:
        score -= 2
        reasons.append("Mercury Retrograde chal raha hai")
    for a in aspects:
        ps = [a["p1"], a["p2"]]
        if "Jupiter" in ps:
            if a["asp"] in ["Trine", "Sextile"]:
                score += 2
                reasons.append(f"Jupiter {a['asp']} positive")
            elif a["asp"] in ["Square", "Opposition"]:
                score -= 1
                reasons.append(f"Jupiter {a['asp']} caution")
        if "Saturn" in ps:
            if a["asp"] in ["Square", "Opposition"]:
                score -= 2
                reasons.append(f"Saturn {a['asp']} pressure")
            elif a["asp"] == "Trine":
                score += 1
                reasons.append(f"Saturn {a['asp']} disciplined")
    if score >= 2.5:
        return "BULLISH", "🟢", round(score,1), reasons
    elif score <= -2:
        return "BEARISH", "🔴", round(score,1), reasons
    return "NEUTRAL", "🟡", round(score,1), reasons

def upcoming_bias(days=10):
    res = []
    base = datetime.now()
    for i in range(days):
        dt = base + timedelta(days=i)
        utc = dt - timedelta(hours=5, minutes=30)
        pos = calc_planets(utc)
        asp = get_aspects(pos)
        sig, emo, sc, _ = get_signal(pos, asp)
        res.append({"date": dt.strftime("%d %b"), "day": dt.strftime("%a"), "sig": sig, "emo": emo, "score": sc, "retro": pos["Mercury"]["retro"]})
    return res

def birth_analysis(dob):
    dt = datetime.combine(dob, datetime.min.time()) + timedelta(hours=12)
    pos = calc_planets(dt)
    lines = [
        f"**Janma Rashi:** {pos['Moon']['sign']}",
        f"**Surya Rashi:** {pos['Sun']['sign']}",
        f"**Nakshatra:** {pos['Moon']['nakshatra']} (Pada {pos['Moon']['pada']})"
    ]
    me = pos["Moon"]["sign_en"]
    if me in ["Cancer", "Pisces", "Scorpio"]:
        lines.append("Swabhav: Emotional & Intuitive")
    elif me in ["Aries", "Leo", "Sagittarius"]:
        lines.append("Swabhav: Aggressive & Risk-taking")
    elif me in ["Taurus", "Virgo", "Capricorn"]:
        lines.append("Swabhav: Practical & Patient")
    else:
        lines.append("Swabhav: Balanced & Analytical")
    return lines, pos

@st.cache_data(ttl=300)
def get_data(symbol, period="3mo"):
    try:
        return yf.Ticker(symbol).history(period=period)
    except:
        return None

def main():
    st.markdown('<div class="main-header">🪐 Astro AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Share Bazaar • Financial Astrology</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Settings")
        selected_date = st.date_input("Date", datetime.now().date())
        selected_time = st.time_input("Time (IST)", datetime.now().time())
        dt = datetime.combine(selected_date, selected_time)
        dt_utc = dt - timedelta(hours=5, minutes=30)

        st.divider()
        st.markdown("### Janam Kundali")
        dob = st.date_input("Date of Birth", value=datetime(1995,1,1).date())

        st.divider()
        market = st.selectbox("Market", ["Nifty 50", "Bank Nifty", "Finnifty", "Sensex", "Reliance", "TCS", "HDFC Bank", "Gold", "Custom"])
        symbols = {
            "Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Finnifty": "NIFTY_FIN_SERVICE.NS",
            "Sensex": "^BSESN", "Reliance": "RELIANCE.NS", "TCS": "TCS.NS",
            "HDFC Bank": "HDFCBANK.NS", "Gold": "GC=F"
        }
        symbol = st.text_input("Symbol", "INFY.NS") if market == "Custom" else symbols.get(market, "^NSEI")
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=1)
        st.caption("Educational purpose only")

    pos = calc_planets(dt_utc)
    aspects = get_aspects(pos)
    signal, emoji, score, reasons = get_signal(pos, aspects)

    c1, c2 = st.columns(2)
    c1.metric("Date", selected_date.strftime("%d %b %Y"))
    c2.metric("Moon", pos["Moon"]["sign"])
    c3, c4 = st.columns(2)
    c3.metric("Signal", f"{emoji} {signal}")
    c4.metric("Score", f"{score:+}")

    if pos["Mercury"]["retro"]:
        st.markdown('<span class="retro-badge">Mercury RETROGRADE</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="direct-badge">Mercury Direct</span>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Planets", "Timing", "Chart", "Kundali", "Info"])

    with tab1:
        st.subheader("Graha Sthiti")
        cols = st.columns(3)
        for i, p in enumerate(["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]):
            if p in pos:
                r = " ℞" if pos[p].get("retro") else ""
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="planet-card">
                        <b>{p}{r}</b><br>
                        {pos[p]['sign']}<br>
                        {pos[p]['degree']:.1f}°<br>
                        <small>{pos[p]['nakshatra']} P{pos[p]['pada']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        if aspects:
            st.subheader("Major Aspects")
            for a in aspects[:8]:
                st.write(f"**{a['p1']}** {a['asp']} **{a['p2']}** (Orb {a['orb']}°)")

    with tab2:
        st.subheader("Aane Wale 10 Din ka Timing")
        upcoming = upcoming_bias(10)
        for d in upcoming:
            cls = {"BULLISH": "day-bullish", "BEARISH": "day-bearish", "NEUTRAL": "day-neutral"}[d["sig"]]
            rt = " | Merc Retro" if d["retro"] else ""
            st.markdown(f'<div class="{cls}"><b>{d["date"]}</b> ({d["day"]}) — {d["emo"]} <b>{d["sig"]}</b> Score: {d["score"]:+}{rt}</div>', unsafe_allow_html=True)
        bull = sum(1 for d in upcoming if d["sig"] == "BULLISH")
        bear = sum(1 for d in upcoming if d["sig"] == "BEARISH")
        neut = sum(1 for d in upcoming if d["sig"] == "NEUTRAL")
        st.write(f"🟢 Bullish: **{bull}** | 🔴 Bearish: **{bear}** | 🟡 Neutral: **{neut}**")

    with tab3:
        st.subheader(f"{market} Chart")
        df = get_data(symbol, period)
        if df is not None and not df.empty:
            cur = df["Close"].iloc[-1]
            prev = df["Close"].iloc[-2] if len(df) > 1 else cur
            chg = cur - prev
            pct = (chg / prev) * 100
            a, b = st.columns(2)
            a.metric("Price", f"₹{cur:,.1f}", f"{chg:+.1f} ({pct:+.2f}%)")
            b.metric("Volume", f"{df['Volume'].iloc[-1]/1e6:.1f}M")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                                                 increasing_line_color="#10b981", decreasing_line_color="#ef4444")])
            fig.update_layout(template="plotly_dark", height=340, margin=dict(l=10,r=10,t=30,b=20),
                              xaxis_rangeslider_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.error("Data nahi mila")

    with tab4:
        st.subheader("Janam Kundali (Basic)")
        lines, bpos = birth_analysis(dob)
        for line in lines:
            st.markdown(f"- {line}")
        st.divider()
        cols = st.columns(3)
        for i, p in enumerate(["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter"]):
            if p in bpos:
                with cols[i % 3]:
                    st.markdown(f'<div class="planet-card"><b>{p}</b><br>{bpos[p]["sign"]}<br><small>{bpos[p]["nakshatra"]}</small></div>', unsafe_allow_html=True)
        st.info("Basic analysis. Exact birth time + place se better hota hai.")

    with tab5:
        st.subheader("About")
        st.markdown("""
        **Astro AI** prototype:
        - Graha Sthiti + Nakshatra
        - Mercury Retrograde
        - 10 din ka Bullish/Bearish/Neutral timing
        - Basic Janam Kundali
        - Live charts
        
        Sirf educational purpose ke liye. Financial advice nahi hai.
        """)

if __name__ == "__main__":
    main()
