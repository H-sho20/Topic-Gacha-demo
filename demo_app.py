import streamlit as st
import requests
from datetime import datetime

# =========================
# 1. 初期設定 & Session State
# =========================
if "demo_history" not in st.session_state:
    st.session_state.demo_history = []
if "gacha_results" not in st.session_state:
    st.session_state.gacha_results = []
if "chosen_topic" not in st.session_state:
    st.session_state.chosen_topic = None
if "toast_queue" not in st.session_state:
    st.session_state.toast_queue = None

WIKI_RANDOM_URL = "https://ja.wikipedia.org/api/rest_v1/page/random/summary"
HEADERS = {"User-Agent": "NoteGachaDemo/2.0"}

st.set_page_config(page_title="お題ガチャ(デモ版)", page_icon="🎰", layout="centered")

# =========================
# 2. CSS (スマホ対応版)
# =========================
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top left, #fff7fb 0%, #fff9f2 45%, #ffffff 100%); }
    .hero-wrap {
        background: linear-gradient(135deg, #ffecf5 0%, #fff4e8 100%);
        border: 1px solid rgba(255, 153, 190, 0.4);
        border-radius: 24px; padding: 2rem; text-align: center; margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(255, 140, 180, 0.15);
    }
    .hero-title { font-size: 2.5rem; font-weight: 900; color: #d94b86; margin-bottom: 0.5rem; }
    .topic-card {
        background: white; border: 1px solid #ffe0eb; border-radius: 20px;
        padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 5px 15px rgba(0,0,0,0.03);
    }
    .topic-title { font-size: 1.3rem; font-weight: bold; color: #8c3e72; margin-bottom: 0.5rem; }
    .topic-extract { font-size: 0.95rem; color: #555; line-height: 1.6; background: #fff9fb; padding: 10px; border-radius: 10px; border-left: 4px solid #ff75a0; }
    .h-card {
        background: white; border: 1px solid #eee; border-radius: 15px;
        padding: 1rem; margin-top: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    .diff-badge { padding: 3px 10px; border-radius: 10px; font-size: 0.75rem; font-weight: bold; }
    .diff-low { background: #e8f5e9; color: #2e7d32; }
    .diff-mid { background: #fffde7; color: #f57f17; }
    .diff-high { background: #ffebee; color: #c62828; }
    
    div[data-testid="stButton"] > button[kind="primary"] {
        min-height: 70px; width: 100%; font-size: 1.5rem; border-radius: 20px;
        background: linear-gradient(90deg, #ff75a0 0%, #ffb56b 100%);
        border: none; color: white; font-weight: 900; box-shadow: 0 8px 20px rgba(255, 117, 160, 0.3);
    }

    @media (max-width: 600px) {
        .hero-title { font-size: 1.6rem !important; }
        .topic-card > div { flex-direction: column !important; }
        .topic-card img {
            width: 100% !important; max-width: 100% !important; height: 180px !important;
            object-fit: cover; margin-bottom: 15px;
        }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"] {
            display: flex !important; flex-direction: row !important;
            flex-wrap: nowrap !important; gap: 8px !important; width: 100% !important;
        }
        div[data-testid="stExpanderDetails"] div[data-testid="stColumn"] {
            flex: 1 1 0 !important; min-width: 0 !important;
        }
        div[data-testid="stExpanderDetails"] div[data-testid="stButton"] > button {
            width: 100% !important; padding: 0.5rem 0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def get_diff_style(diff):
    if diff <= 2: return "diff-low", "初級"
    if diff <= 3: return "diff-mid", "中級"
    return "diff-high", "上級"

# =========================
# 3. メイン表示エリア
# =========================
if st.session_state.toast_queue:
    msg, icon = st.session_state.toast_queue
    st.toast(msg, icon=icon)
    st.session_state.toast_queue = None

st.markdown('<div class="hero-wrap"><div class="hero-title">🎰 お題ガチャ</div><p>【デモ版】ブラウザを閉じると履歴は消去されます</p></div>', unsafe_allow_html=True)

# ガチャボタン
if st.button("🎰 運命のお題を3つ引く！", type="primary"):
    with st.spinner("面白いネタを探しています..."):
        res_list = []
        max_retry = 30  # 失敗時のリトライ回数を増やす
        i = 0
        while len(res_list) < 3 and i < max_retry:
            try:
                r = requests.get(WIKI_RANDOM_URL, headers=HEADERS, timeout=5).json()
                if "title" in r:
                    # 同じタイトルの重複を防ぐ
                    if r["title"] not in [x["title"] for x in res_list]:
                        res_list.append({
                            "title": r["title"], "url": r["content_urls"]["desktop"]["page"],
                            "extract": r.get("extract", "詳細なし"),
                            "thumb": r.get("thumbnail", {}).get("source", ""),
                            "diff": min(max(len(r.get("extract", "")) // 150 + 1, 1), 5)
                        })
            except:
                pass
            i += 1
        st.session_state.gacha_results = res_list
        st.session_state.chosen_topic = None
    st.rerun()

# ガチャ結果表示
if st.session_state.gacha_results and not st.session_state.chosen_topic:
    st.write("### ✨ 今日のピックアップ候補")
    for idx, t in enumerate(st.session_state.gacha_results):
        d_cls, d_lbl = get_diff_style(t['diff'])
        st.markdown(f"""
        <div class="topic-card">
            <div style="display:flex; gap:20px; align-items:start;">
                <img src="{t['thumb'] if t['thumb'] else 'https://via.placeholder.com/100x100?text=No+Image'}" 
                     style="width:100%; max-width:100px; aspect-ratio:1/1; object-fit:cover; border-radius:12px; border:1px solid #eee;">
                <div style="flex:1;">
                    <div class="topic-title">{t['title']} <span class="diff-badge {d_cls}">★{t['diff']} {d_lbl}</span></div>
                    <div class="topic-extract"><b>【詳細】</b><br>{t['extract'][:200]}...</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"👉 『{t['title']}』を執筆お題にする！", key=f"sel_{idx}", use_container_width=True):
            new_data = {
                "id": datetime.now().timestamp(),
                "title": t['title'], "url": t['url'], "difficulty": t['diff'],
                "thumbnail": t['thumb'], "extract": t['extract'],
                "is_favorite": False, "is_written": False, "note": "",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.demo_history.insert(0, new_data)
            st.session_state.chosen_topic = t
            # ここでは風船を出さず、トーストのみ
            st.session_state.toast_queue = (f"「{t['title']}」を追加しました", "✍️")
            st.rerun()

if st.session_state.get("chosen_topic"):
    # お題決定時も風船を削除
    st.success("お題が決定しました！ 下の履歴から詳細を確認・編集できます。")
    if st.button("他の候補も見る / 引き直す"):
        st.session_state.chosen_topic = None; st.rerun()

# =========================
# 4. 履歴表示
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.write("### 🗂 デモ用・一時履歴")

if st.session_state.demo_history:
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        filter_mode = st.radio("表示フィルタ", ["すべて", "お気に入り❤️", "未執筆のみ"], horizontal=True)
    with f_col2:
        if st.button("🗑️ 履歴をリセット"):
            st.session_state.demo_history = []
            st.rerun()

    for idx, row in enumerate(st.session_state.demo_history):
        if filter_mode == "お気に入り❤️" and not row['is_favorite']: continue
        if filter_mode == "未執筆のみ" and row['is_written']: continue
        
        d_cls, d_lbl = get_diff_style(row['difficulty'])
        st.markdown(f"""
        <div class="h-card">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#999;">
                <span>{row['created_at'][:10]} 追加</span>
                <span>{'❤️' if row['is_favorite'] else ''} {'✅' if row['is_written'] else ''}</span>
            </div>
            <div style="margin: 8px 0;">
                <a href="{row['url']}" target="_blank" style="font-weight:bold; color:#d94b86; text-decoration:none; font-size:1.15rem;">{row['title']}</a>
                <span class="diff-badge {d_cls}">★{row['difficulty']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("意味・詳細・メモを開く"):
            st.info(f"**【意味・詳細】**\n\n{row['extract']}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                fav_label = "❤️" if row['is_favorite'] else "🤍"
                if st.button(fav_label, key=f"fav_{idx}", use_container_width=True):
                    row['is_favorite'] = not row['is_favorite']
                    # お気に入り時もトーストのみ
                    st.session_state.toast_queue = ("お気に入りを更新", "❤️")
                    st.rerun()
            with c2:
                # 執筆完了ボタン
                done_label = "✅" if row['is_written'] else "⬜"
                if st.button(done_label, key=f"done_{idx}", use_container_width=True):
                    # 未完了から完了に変わる瞬間だけ風船を出す
                    if not row['is_written']:
                        st.balloons()
                        st.session_state.toast_queue = ("執筆完了！お疲れ様です！", "🎉")
                    row['is_written'] = not row['is_written']
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                    st.session_state.demo_history.pop(idx); st.rerun()
            
            st.markdown("<div style='font-size:0.85rem; color:#555; margin-top:10px;'>構成案・メモ</div>", unsafe_allow_html=True)
            new_note = st.text_input("メモ", value=row['note'], key=f"note_{idx}", placeholder="メモを記入...", label_visibility="collapsed")
            if new_note != row['note']:
                row['note'] = new_note
                st.session_state.toast_queue = ("メモを保存しました", "📝")
                st.rerun()
else:
    st.info("ここに一時的な履歴が表示されます。")