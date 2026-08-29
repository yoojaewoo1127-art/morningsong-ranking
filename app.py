import streamlit as st
import requests
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="SSHS 기상곡 리더보드",
    page_icon="🎵",
    layout="wide"
)

# 2. 커스텀 CSS 적용
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #f4f6f9;
    }

    .main-title {
        text-align: center;
        padding: 10px 0 20px 0;
    }
    .main-title h1 {
        font-size: 28px;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .main-title p {
        color: #64748b;
        font-size: 14px;
    }

    /* 카드 컨테이너 */
    .ranking-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 18px 16px 14px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .card-title {
        font-size: 15px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 12px;
    }

    /* 1등 히어로 영역 */
    .hero-section {
        text-align: center;
        padding-bottom: 14px;
        border-bottom: 1px solid #f1f5f9;
        position: relative;
    }

    .gold-badge {
        position: absolute;
        top: 0px;
        left: 8px;
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #ffffff;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        font-size: 13px;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 5px rgba(217, 119, 6, 0.3);
    }

    .hero-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #f8fafc;
        box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        margin-bottom: 6px;
    }

    .hero-name {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
    }

    .hero-score {
        font-size: 18px;
        font-weight: 800;
        color: #2563eb;
        margin-top: 2px;
    }

    .hero-score.danger {
        color: #ef4444;
    }

    /* 2~5위 리스트 영역 */
    .sub-list {
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .sub-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 2px;
    }

    .sub-left {
        display: flex;
        align-items: center;
        gap: 10px;
        overflow: hidden;
    }

    .sub-rank {
        font-size: 13px;
        font-weight: 700;
        color: #94a3b8;
        width: 14px;
        text-align: center;
    }

    .sub-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid #e2e8f0;
        flex-shrink: 0;
    }

    .sub-name {
        font-size: 13px;
        font-weight: 600;
        color: #334155;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 95px;
    }

    .sub-score {
        font-size: 13px;
        font-weight: 700;
        color: #1e293b;
        flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로딩
@st.cache_data(ttl=300)
def load_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    songs = requests.get("https://sshs.app/api/morningsong", headers=headers).json()
    users = requests.get("https://sshs.app/api/users", headers=headers).json()
    
    df_songs = pd.DataFrame(songs)
    default_pfp = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
    
    user_meta = {}
    for u in users:
        sid = u.get("student_id")
        if sid:
            raw_name = u.get("name", str(sid))
            clean_name = raw_name.split(" ")[-1] if " " in raw_name else raw_name
            pfp = u.get("pfp_url") if u.get("pfp_url") else default_pfp
            user_meta[int(sid)] = {"name": clean_name, "pfp": pfp}
            
    df_songs['proposer'] = pd.to_numeric(df_songs['proposer'], errors='coerce')
    df_songs['agree'] = pd.to_numeric(df_songs['agree'], errors='coerce').fillna(0).astype(int)
    df_songs['disagree'] = pd.to_numeric(df_songs['disagree'], errors='coerce').fillna(0).astype(int)
    df_songs['net_votes'] = df_songs['agree'] - df_songs['disagree']
    
    return df_songs, user_meta, default_pfp

try:
    df_songs, user_meta, default_pfp = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

def get_user(pid):
    if pd.isna(pid):
        return {"name": "알 수 없음", "pfp": default_pfp}
    return user_meta.get(int(pid), {"name": f"학생({int(pid)})", "pfp": default_pfp})

# 4. 카드 렌더링 함수
def render_leaderboard_card(title, df_rank, val_col, unit="", is_danger=False):
    if df_rank.empty:
        st.markdown(f"<div class='ranking-card'><div class='card-title'>{title}</div><p style='color:#94a3b8;'>기록 없음</p></div>", unsafe_allow_html=True)
        return

    top1 = df_rank.iloc[0]
    top1_info = get_user(top1['proposer'])
    top1_val = top1[val_col]
    top1_val_str = f"+{top1_val}" if unit == "점" and top1_val > 0 else f"{top1_val}"
    score_cls = "hero-score danger" if is_danger else "hero-score"

    sub_items_html = ""
    for rank_num, row in enumerate(df_rank.iloc[1:5].itertuples(), start=2):
        u_info = get_user(getattr(row, 'proposer'))
        val = getattr(row, val_col)
        val_str = f"+{val}" if unit == "점" and val > 0 else f"{val}"
        
        # HTML 태그 내 줄바꿈을 제거하여 Streamlit 마크다운 파서 오작동 방지
        sub_items_html += f"<div class='sub-item'><div class='sub-left'><span class='sub-rank'>{rank_num}</span><img class='sub-avatar' src='{u_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/><span class='sub-name' title='{u_info['name']}'>{u_info['name']}</span></div><span class='sub-score'>{val_str}{unit}</span></div>"

    card_html = f"<div class='ranking-card'><div class='card-title'>{title}</div><div class='hero-section'><div class='gold-badge'>1</div><img class='hero-avatar' src='{top1_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/><div class='hero-name'>{top1_info['name']}</div><div class='{score_cls}'>{top1_val_str}{unit}</div></div><div class='sub-list'>{sub_items_html}</div></div>"
    
    st.markdown(card_html, unsafe_allow_html=True)

# 5. 각 항목별 순위 계산
likes_df = df_songs.groupby('proposer')['agree'].sum().reset_index().sort_values(by='agree', ascending=False).reset_index(drop=True)
net_high_df = df_songs.groupby('proposer')['net_votes'].sum().reset_index().sort_values(by='net_votes', ascending=False).reset_index(drop=True)
app_df = df_songs[df_songs['approved'] == True].groupby('proposer').size().reset_index(name='app_cnt').sort_values(by='app_cnt', ascending=False).reset_index(drop=True)

top_weekly = df_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, False]).groupby(['year', 'week']).first().reset_index()
first_cnt_df = top_weekly.groupby('proposer').size().reset_index(name='first_cnt').sort_values(by='first_cnt', ascending=False).reset_index(drop=True)

dislikes_df = df_songs.groupby('proposer')['disagree'].sum().reset_index().sort_values(by='disagree', ascending=False).reset_index(drop=True)
net_low_df = df_songs.groupby('proposer')['net_votes'].sum().reset_index().sort_values(by='net_votes', ascending=True).reset_index(drop=True)

bot_weekly = df_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, True]).groupby(['year', 'week']).first().reset_index()
last_cnt_df = bot_weekly.groupby('proposer').size().reset_index(name='last_cnt').sort_values(by='last_cnt', ascending=False).reset_index(drop=True)

rej_df = df_songs[df_songs['approved'] == False].groupby('proposer').size().reset_index(name='rej_cnt').sort_values(by='rej_cnt', ascending=False).reset_index(drop=True)

# 6. 화면 헤더 및 탭
st.markdown("""
<div class="main-title">
    <h1>🏆 SSHS 기상곡 명예의 전당</h1>
    <p>실시간 부문별 1위~5위 순위표</p>
</div>
""", unsafe_allow_html=True)

tab_honor, tab_dishonor = st.tabs(["🏅 명예 기록", "💀 불명예 기록"])

with tab_honor:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_leaderboard_card("❤️ 최다 좋아요", likes_df, 'agree', '개')
    with c2:
        render_leaderboard_card("🔥 최고 순합산 (Net)", net_high_df, 'net_votes', '점')
    with c3:
        render_leaderboard_card("🎉 최다 곡 승인", app_df, 'app_cnt', '곡')
    with c4:
        render_leaderboard_card("🥇 주별 1위 최다", first_cnt_df, 'first_cnt', '회')

with tab_dishonor:
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        render_leaderboard_card("💔 최다 싫어요", dislikes_df, 'disagree', '개', is_danger=True)
    with d2:
        render_leaderboard_card("❄️ 최저 순합산 (Net)", net_low_df, 'net_votes', '점', is_danger=True)
    with d3:
        render_leaderboard_card("📉 주별 꼴등 최다", last_cnt_df, 'last_cnt', '회', is_danger=True)
    with d4:
        render_leaderboard_card("🚫 최다 승인 탈락", rej_df, 'rej_cnt', '곡', is_danger=True)
