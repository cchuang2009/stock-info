import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import calendar

st.set_page_config(
    page_title="美股財報日曆",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Page background: warm off-white, easy on the eyes ── */
.main { background-color: #f5f6fa; }
[data-testid="stAppViewContainer"] { background: #f5f6fa; }
[data-testid="stMainBlockContainer"] { background: #f5f6fa; }

/* ── Sidebar: soft slate blue-grey ── */
[data-testid="stSidebar"] { background: #eef0f7 !important; border-right: 1px solid #d8dce8; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #374151 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #1d4ed8 !important; }

/* ── Headings ── */
h1, h2, h3 { color: #1e3a5f !important; font-family: 'Inter', sans-serif !important; font-weight: 700 !important; }

/* ── Buttons ── */
.stButton>button {
    background: #1d4ed8; color: #ffffff;
    border: none; border-radius: 6px;
    font-family: 'Inter', sans-serif; font-weight: 600; font-size: 13px;
    padding: 6px 18px; transition: background 0.15s;
}
.stButton>button:hover { background: #1e40af; }

/* ── All inputs / selects / textareas ── */
.stTextInput>div>div>input,
.stSelectbox>div>div>select,
.stDateInput>div>div>input,
.stTextArea>div>div>textarea {
    background: #ffffff !important;
    color: #1f2937 !important;
    border: 1.5px solid #c7cde0 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color: #1d4ed8 !important;
    box-shadow: 0 0 0 3px #dbeafe !important;
}
/* placeholder colour */
.stTextInput>div>div>input::placeholder,
.stTextArea>div>div>textarea::placeholder { color: #9ca3af !important; font-style: italic; }

/* label text above inputs */
.stTextInput label, .stSelectbox label, .stDateInput label,
.stTextArea label, .stRadio label { color: #374151 !important; font-weight: 600 !important; font-size: 13px !important; }

/* ── Calendar table ── */
.cal-table { width: 100%; border-collapse: separate; border-spacing: 3px; font-family: 'Inter', sans-serif; }
.cal-table th {
    background: #e8eaf3; color: #6b7280; font-size: 12px; font-weight: 700;
    letter-spacing: .06em; text-align: center; padding: 10px 4px;
    border-radius: 4px;
}
.cal-table td {
    vertical-align: top; padding: 7px 6px;
    background: #ffffff; border-radius: 6px;
    border: 1px solid #e5e7eb;
    min-height: 86px; min-width: 110px;
    box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.cal-table td.today-cell { border: 2px solid #1d4ed8 !important; background: #eff6ff; }
.cal-table td.empty-cell { background: #f0f1f6; border-color: #e8eaf3; box-shadow: none; }
.day-num { font-size: 12px; color: #9ca3af; font-weight: 500; margin-bottom: 5px; }
.day-num.today { color: #1d4ed8; font-weight: 700; }

/* ── Earning chips (light palette) ── */
.earn-chip { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px;
    margin-bottom: 3px; display: block; letter-spacing:.03em; font-family:'IBM Plex Mono',monospace; }
.earn-pre  { background:#e0f7fa; color:#0277bd; border:1px solid #b3e5fc; }
.earn-post { background:#fff8e1; color:#e65100; border:1px solid #ffe0b2; }
.earn-mid  { background:#f3e5f5; color:#6a1b9a; border:1px solid #e1bee7; }
.earn-unk  { background:#f1f3f5; color:#6b7280; border:1px solid #d1d5db; }

/* ── Legend ── */
.legend-item { display:inline-flex; align-items:center; gap:6px; margin-right:20px; font-size:12px; color:#6b7280; }
.legend-dot { width:11px; height:11px; border-radius:3px; display:inline-block; }

/* ── Metric cards ── */
.metric-card {
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 16px 20px; text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.metric-num { font-size: 28px; font-weight: 700; color: #1d4ed8; font-family: 'IBM Plex Mono', monospace; }
.metric-label { font-size: 11px; color: #9ca3af; letter-spacing:.08em; text-transform:uppercase; margin-top:4px; }

/* ── Form container ── */
[data-testid="stForm"] {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #e5e7eb !important; border-radius: 8px; background: #fff; }

/* ── Selectbox dropdown ── */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #ffffff !important; border: 1.5px solid #c7cde0 !important; border-radius: 6px !important;
    color: #1f2937 !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label { color: #374151 !important; }

/* ── Divider ── */
hr { border-color: #e5e7eb !important; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "earnings_data.json"

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # seed data
    return {
        "2025-04": [
            {"id":"a1","date":"2025-04-23","ticker":"TSLA","name":"Tesla","time":"盤後","notes":"Q1 2025，關注毛利率與FSD進展"},
            {"id":"a2","date":"2025-04-24","ticker":"META","name":"Meta Platforms","time":"盤後","notes":"廣告收入、AI資本支出"},
            {"id":"a3","date":"2025-04-25","ticker":"MSFT","name":"Microsoft","time":"盤後","notes":"Azure成長率、Copilot滲透"},
            {"id":"a4","date":"2025-04-25","ticker":"GOOGL","name":"Alphabet","time":"盤後","notes":"搜尋廣告 vs AI競爭"},
            {"id":"a5","date":"2025-04-30","ticker":"AAPL","name":"Apple","time":"盤後","notes":"iPhone銷量、服務收入"},
        ],
        "2025-05": [
            {"id":"b1","date":"2025-05-01","ticker":"AMZN","name":"Amazon","time":"盤後","notes":"AWS成長率、零售毛利"},
            {"id":"b2","date":"2025-05-14","ticker":"NVDA","name":"NVIDIA","time":"盤後","notes":"Blackwell出貨、數據中心需求"},
            {"id":"b3","date":"2025-05-21","ticker":"AAOI","name":"Applied Optoelectronics","time":"盤後","notes":"光通訊需求、400G/800G進展"},
            {"id":"b4","date":"2025-05-22","ticker":"COHR","name":"Coherent Corp","time":"盤後","notes":"光模組出貨、AI需求能見度"},
        ],
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_month_key(y, m):
    return f"{y}-{m:02d}"

def gen_id():
    import uuid
    return uuid.uuid4().hex[:8]

def chip_class(time_str):
    return {"盤前":"earn-pre","盤後":"earn-post","盤中":"earn-mid"}.get(time_str,"earn-unk")

# ── Session state ─────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "edit_entry" not in st.session_state:
    st.session_state.edit_entry = None

data = st.session_state.data

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 財報日曆")
    st.markdown("---")

    now = datetime.now()
    years  = list(range(now.year - 1, now.year + 4))
    months = list(range(1, 13))
    MONTHS_ZH = ["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"]

    sel_year  = st.selectbox("年份", years,  index=years.index(now.year))
    sel_month = st.selectbox("月份", months, index=months.index(now.month),
                              format_func=lambda m: f"{m:02d} {MONTHS_ZH[m-1]}")

    st.markdown("---")
    view_mode = st.radio("顯示模式", ["📅 月曆", "📋 清單"], horizontal=True)
    st.markdown("---")

    # ── GitHub Sync ──
    with st.expander("🔗 GitHub 同步", expanded=False):
        gh_token = st.text_input("GitHub Token (PAT)", type="password", placeholder="ghp_xxxx")
        gh_repo  = st.text_input("Repo (user/repo)",   placeholder="yourname/earnings-data")
        gh_path  = st.text_input("檔案路徑",            value="earnings_data.json")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("⬇ Pull", use_container_width=True):
                if gh_token and gh_repo:
                    try:
                        import requests, base64
                        url = f"https://api.github.com/repos/{gh_repo}/contents/{gh_path}"
                        r = requests.get(url, headers={"Authorization":f"token {gh_token}"}, timeout=8)
                        if r.status_code == 200:
                            content = base64.b64decode(r.json()["content"]).decode("utf-8")
                            st.session_state.data = json.loads(content)
                            save_data(st.session_state.data)
                            st.success("✅ 已同步")
                            st.rerun()
                        else:
                            st.error(f"錯誤 {r.status_code}")
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.warning("請填寫 Token 與 Repo")
        with col_g2:
            if st.button("⬆ Push", use_container_width=True):
                if gh_token and gh_repo:
                    try:
                        import requests, base64
                        url = f"https://api.github.com/repos/{gh_repo}/contents/{gh_path}"
                        r = requests.get(url, headers={"Authorization":f"token {gh_token}"}, timeout=8)
                        sha = r.json().get("sha","") if r.status_code==200 else ""
                        content = base64.b64encode(json.dumps(data,ensure_ascii=False,indent=2).encode()).decode()
                        payload = {"message":"Update earnings data","content":content}
                        if sha: payload["sha"] = sha
                        r2 = requests.put(url, headers={"Authorization":f"token {gh_token}"},
                                          json=payload, timeout=8)
                        if r2.status_code in (200,201):
                            st.success("✅ 已推送")
                        else:
                            st.error(f"錯誤 {r2.status_code}")
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.warning("請填寫 Token 與 Repo")

    st.markdown("---")
    # Download
    month_key = get_month_key(sel_year, sel_month)
    month_list = data.get(month_key, [])

    if month_list:
        df_dl = pd.DataFrame(month_list)[["date","ticker","name","time","notes"]]
        df_dl.columns = ["日期","標的","公司","時間","財資消息"]
        csv_bytes = df_dl.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇ 下載本月 CSV", csv_bytes,
                           f"earnings_{month_key}.csv", "text/csv", use_container_width=True)

    all_flat = [e for lst in data.values() for e in lst]
    if all_flat:
        df_all = pd.DataFrame(all_flat)[["date","ticker","name","time","notes"]]
        df_all.columns = ["日期","標的","公司","時間","財資消息"]
        csv_all = df_all.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇ 下載全部 CSV", csv_all,
                           "earnings_all.csv", "text/csv", use_container_width=True)
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("⬇ 下載 JSON", json_bytes,
                       "earnings_all.json", "application/json", use_container_width=True)

# ── Main ──────────────────────────────────────────────────────────────────────
month_key  = get_month_key(sel_year, sel_month)
month_list = data.get(month_key, [])
month_list_sorted = sorted(month_list, key=lambda e: e["date"])

col_title, col_nav = st.columns([3,1])
with col_title:
    st.markdown(f"## 📅 {sel_year} 年 {MONTHS_ZH[sel_month-1]}　財報日曆")
with col_nav:
    st.markdown(f"<div style='text-align:right;padding-top:14px;color:#475569;font-size:13px;'>共 <b style='color:#38bdf8'>{len(month_list)}</b> 筆財報</div>", unsafe_allow_html=True)

# metrics
m1, m2, m3, m4 = st.columns(4)
pre_cnt  = sum(1 for e in month_list if e.get("time")=="盤前")
post_cnt = sum(1 for e in month_list if e.get("time")=="盤後")
mid_cnt  = sum(1 for e in month_list if e.get("time")=="盤中")
tickers  = list(set(e["ticker"] for e in month_list))
m1.markdown(f'<div class="metric-card"><div class="metric-num">{len(month_list)}</div><div class="metric-label">本月財報</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#22d3ee">{pre_cnt}</div><div class="metric-label">盤前</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#f59e0b">{post_cnt}</div><div class="metric-label">盤後</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#a78bfa">{mid_cnt}</div><div class="metric-label">盤中</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CALENDAR VIEW ─────────────────────────────────────────────────────────────
if view_mode == "📅 月曆":
    # build day→entries map
    day_map = {}
    for e in month_list:
        d = int(e["date"].split("-")[2])
        day_map.setdefault(d, []).append(e)

    first_weekday, days_in_month = calendar.monthrange(sel_year, sel_month)
    # 0=Mon…6=Sun → shift to Sun-first
    first_weekday = (first_weekday + 1) % 7

    DAY_NAMES = ["日","一","二","三","四","五","六"]
    today = date.today()

    cells = [None]*first_weekday + list(range(1, days_in_month+1))
    while len(cells) % 7: cells.append(None)

    html = '<table class="cal-table"><thead><tr>'
    for dn in DAY_NAMES:
        html += f'<th>{dn}</th>'
    html += '</tr></thead><tbody>'

    for i, day in enumerate(cells):
        if i % 7 == 0: html += '<tr>'
        if day is None:
            html += '<td class="empty-cell"></td>'
        else:
            is_today = (sel_year==today.year and sel_month==today.month and day==today.day)
            td_class = "today-cell" if is_today else ""
            dn_class = "today" if is_today else ""
            html += f'<td class="{td_class}"><div class="day-num {dn_class}">{day}</div>'
            for e in day_map.get(day, []):
                cc = chip_class(e.get("time",""))
                html += f'<span class="earn-chip {cc}" title="{e.get("name","")} | {e.get("time","")} | {e.get("notes","")}">{e["ticker"]}</span>'
            html += '</td>'
        if i % 7 == 6: html += '</tr>'

    html += '</tbody></table>'
    html += '''<div style="margin-top:12px;">
      <span class="legend-item"><span class="legend-dot" style="background:#0e3a4a;border:1px solid #22d3ee"></span>盤前</span>
      <span class="legend-item"><span class="legend-dot" style="background:#4a2e06;border:1px solid #f59e0b"></span>盤後</span>
      <span class="legend-item"><span class="legend-dot" style="background:#2d1a4a;border:1px solid #a78bfa"></span>盤中</span>
      <span class="legend-item"><span class="legend-dot" style="background:#1e293b;border:1px solid #475569"></span>未確認</span>
    </div>'''
    st.markdown(html, unsafe_allow_html=True)

# ── LIST VIEW ─────────────────────────────────────────────────────────────────
else:
    search = st.text_input("🔍 搜尋標的 / 公司", placeholder="e.g. NVDA 或 NVIDIA")
    display_list = month_list_sorted
    if search:
        s = search.lower()
        display_list = [e for e in display_list if s in e["ticker"].lower() or s in e.get("name","").lower()]

    if not display_list:
        st.info("本月尚無財報資料，請使用下方表單新增。")
    else:
        df_show = pd.DataFrame(display_list)
        df_show = df_show[["date","ticker","name","time","notes"]].copy()
        df_show.columns = ["日期","標的","公司名稱","時間","財資消息"]
        st.dataframe(df_show, use_container_width=True, hide_index=True,
                     column_config={
                         "日期": st.column_config.DateColumn("日期", width="small"),
                         "標的": st.column_config.TextColumn("標的", width="small"),
                         "時間": st.column_config.TextColumn("時間", width="small"),
                         "財資消息": st.column_config.TextColumn("財資消息", width="large"),
                     })

# ── ADD / EDIT FORM ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ✏️ 新增 / 編輯財報")

edit = st.session_state.edit_entry
prefill = edit if edit else {}

# populate edit from list
edit_ticker_list = ["(新增)"] + sorted(set(e["ticker"] for e in month_list_sorted))
edit_choice = st.selectbox("選擇已有標的來編輯（或選新增）", edit_ticker_list)

if edit_choice != "(新增)":
    matches = [e for e in month_list_sorted if e["ticker"]==edit_choice]
    if matches: prefill = matches[0]

with st.form("earn_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        f_date = st.date_input("📅 財報日期 *",
                               value=date.fromisoformat(prefill["date"]) if prefill.get("date") else date(sel_year, sel_month, 1))
    with col2:
        f_ticker = st.text_input("📌 標的 (Ticker) *", value=prefill.get("ticker",""), placeholder="e.g. NVDA")
    with col3:
        f_time = st.selectbox("🕐 公布時間", ["盤後","盤前","盤中","未確認"],
                              index=["盤後","盤前","盤中","未確認"].index(prefill.get("time","盤後")))

    col4, col5 = st.columns([2,4])
    with col4:
        f_name = st.text_input("🏢 公司名稱", value=prefill.get("name",""), placeholder="e.g. NVIDIA Corporation")
    with col5:
        f_notes = st.text_area("📝 財資消息 / 備註", value=prefill.get("notes",""),
                               placeholder="關注重點、EPS共識、指引預期...", height=80)

    col_s, col_d, _ = st.columns([1,1,4])
    with col_s:
        submitted = st.form_submit_button("💾 儲存", use_container_width=True, type="primary")
    with col_d:
        delete_btn = st.form_submit_button("🗑 刪除此標的", use_container_width=True)

    if submitted:
        if not f_ticker:
            st.error("請填寫標的代碼")
        else:
            key = f_date.strftime("%Y-%m")
            ticker_upper = f_ticker.strip().upper()
            entry = {"id": prefill.get("id", gen_id()),
                     "date": str(f_date), "ticker": ticker_upper,
                     "name": f_name.strip(), "time": f_time, "notes": f_notes.strip()}
            lst = data.get(key, [])
            idx = next((i for i,e in enumerate(lst) if e["ticker"]==ticker_upper), None)
            if idx is not None:
                lst[idx] = entry
            else:
                lst.append(entry)
            data[key] = lst
            save_data(data)
            st.session_state.edit_entry = None
            st.success(f"✅ 已儲存 {ticker_upper} ({str(f_date)})")
            st.rerun()

    if delete_btn and edit_choice != "(新增)":
        key = prefill.get("date","")[:7] if prefill.get("date") else month_key
        data[key] = [e for e in data.get(key,[]) if e["ticker"]!=edit_choice]
        save_data(data)
        st.success(f"🗑 已刪除 {edit_choice}")
        st.rerun()
