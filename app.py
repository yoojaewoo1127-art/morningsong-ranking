import streamlit as st
import requests
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="기상곡 명예의 전당",
    page_icon="🎵",
    layout="wide"
)

# 야구 리더보드 스타일 커스텀 CSS 적용
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #f0f3f8;
    }

    .header-box {
        text-align: center;
        padding: 24px 0 10px 0;
    }

    .header-box h1 {
        font-size: 28px;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 6px;
    }

    .header-box p {
        color: #64748b;
        font-size: 14px;
    }

    /* 카드 스타일 */
    .leaderboard-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px 16px 16px 16px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        border: 1px solid #e8edf4;
        display: flex;
        flex-direction: column;
        height: 100%;
        margin-bottom: 20px;
    }

    .category-title {
        font-size: 15px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* 1등 하이라이트 영역 */
    .top-rank-hero {
        text-align: center;
        padding: 10px 0 16px 0;
        border-bottom: 1px solid #f1f5f9;
        position: relative;
    }

    .gold-badge {
        position: absolute;
        top: 0px;
        left: 12px;
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #fff;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        font-size: 13px;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(217, 119, 6, 0.4);
    }

    .hero-avatar-wrapper {
        position: relative;
        display: inline-block;
        margin-bottom: 8px;
    }

    .hero-avatar {
        width: 76px;
        height: 76px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #f8fafc;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    .hero-name {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .hero-score {
        font-size: 20px;
        font-weight: 800;
        color: #2563eb;
    }

    /* 2~5등 리스트 영역 */
    .rank-list {
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        flex-grow: 1;
    }

    .rank-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 4px;
    }

    .rank-left {
        display: flex;
        align-items: center;
        gap: 10px;
        overflow: hidden;
    }

    .rank-num {
        font-size: 13px;
        font-weight: 700;
        color: #94a3b8;
        width: 14px;
        text-align: center;
    }

    .sub-avatar {
        width: 34px;
        height: 34px;
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

    .rank-score {
        font-size: 13px;
        font-weight: 700;
        color: #1e293b;
        flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로딩 및 캐싱 함수
@st.cache_data(ttl=300)
def fetch_and_process_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    songs_res = requests.get("https://sshs.app/api/morningsong", headers=headers)
    users_res = requests.get("https://sshs.app/api/users", headers=headers)
    
    songs = songs_res.json()
    users = users_res.json()
    
    df_songs = pd.DataFrame(songs)
    df_users = pd.DataFrame(users)
    
    # 기본 프로필 이미지 설정
    default_pfp = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
    
    # 유저 사전 생성: {student_id: {"name": ..., "pfp": ...}}
    user_meta = {}
    for u in users:
        sid = u.get("student_id")
        if sid:
            raw_name = u.get("name", str(sid))
            # '(35기) 23051 심재민' -> '심재민' 처럼 깔끔하게 파싱 (원형 보존도 가능)
            clean_name = raw_name.split(" ")[-1] if " " in raw_name else raw_name
            pfp = u.get("pfp_url") if u.get("pfp_url") else default_pfp
            user_meta[int(sid)] = {"name": clean_name, "full_name": raw_name, "pfp": pfp}
            
    df_songs['proposer'] = pd.to_numeric(df_songs['proposer'], errors='coerce')
    df_songs['agree'] = pd.to_numeric(df_songs['agree'], errors='coerce').fillna(0).astype(int)
    df_songs['disagree'] = pd.to_numeric(df_songs['disagree'], errors='coerce').fillna(0).astype(int)
    df_songs['net_votes'] = df_songs['agree'] - df_songs['disagree']
    
    return df_songs, user_meta, default_pfp

# 데이터 로드
try:
    df_songs, user_meta, default_pfp = fetch_and_process_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 이름 & 아바타 매핑 도우미 함수
def get_user_info(proposer_id):
    if pd.isna(proposer_id):
        return {"name": "알 수 없음", "pfp": default_pfp}
    pid = int(proposer_id)
    return user_meta.get(pid, {"name": f"학생({pid})", "pfp": default_pfp})

# 1. 최다 좋아요 집계
likes_df = df_songs.groupby('proposer')['agree'].sum().reset_index()
likes_df = likes_df.sort_values(by='agree', ascending=False).reset_index(drop=True)

# 2. 최다 싫어요 집계
dislikes_df = df_songs.groupby('proposer')['disagree'].sum().reset_index()
dislikes_df = dislikes_df.sort_values(by='disagree', ascending=False).reset_index(drop=True)

# 3. 최다 합산 (좋아요 - 싫어요) 집계
net_df = df_songs.groupby('proposer')['net_votes'].sum().reset_index()
net_df = net_df.sort_values(by='net_votes', ascending=False).reset_index(drop=True)

# 4. 최다 기상곡 승인 (approved == True)
app_df = df_songs[df_songs['approved'] == True].groupby('proposer').size().reset_index(name='approved_cnt')
app_df = app_df.sort_values(by='approved_cnt', ascending=False).reset_index(drop=True)

# 5. 최다 1등 횟수 집계
df_sorted_desc = df_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, False])
weekly_1st = df_sorted_desc.groupby(['year', 'week']).first().reset_index()
first_df = weekly_1st.groupby('proposer').size().reset_index(name='first_cnt')
first_df = first_df.sort_values(by='first_cnt', ascending=False).reset_index(drop=True)

# 6. 최다 꼴등 횟수 집계
df_sorted_asc = df_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, True])
weekly_last = df_sorted_asc.groupby(['year', 'week']).first().reset_index()
last_df = weekly_last.groupby('proposer').size().reset_index(name='last_cnt')
last_df = last_df.sort_values(by='last_cnt', ascending=False).reset_index(drop=True)

# 카드 렌더링 헬퍼 함수
def render_card(title, df_rank, val_col, unit=""):
    if df_rank.empty:
        st.markdown(f"<div class='leaderboard-card'><div class='category-title'>{title}</div><p style='color:#94a3b8; font-size:13px;'>데이터 없음</p></div>", unsafe_allow_html=True)
        return

    # 1등 정보
    top1_id = df_rank.iloc[0]['proposer']
    top1_val = df_rank.iloc[0][val_col]
    top1_info = get_user_info(top1_id)
    
    # 2~5등 리스트 구성
    sub_rows_html = ""
    for rank, row in enumerate(df_rank.iloc[1:5].itertuples(), start=2):
        u_info = get_user_info(getattr(row, 'proposer'))
        val = getattr(row, val_col)
        # 0보다 큰 양수 부호 포맷팅 (합산 전용)
        val_str = f"+{val}" if unit == "점" and val > 0 else f"{val}"
        
        sub_rows_html += f"""
        <div class="rank-item">
            <div class="rank-left">
                <span class="rank-num">{rank}</span>
                <img class="sub-avatar" src="{u_info['pfp']}" onerror="this.src='{default_pfp}';"/>
                <span class="sub-name" title="{u_info['name']}">{u_info['name']}</span>
            </div>
            <span class="rank-score">{val_str}{unit}</span>
        </div>
        """

    top1_val_str = f"+{top1_val}" if unit == "점" and top1_val > 0 else f"{top1_val}"

    card_html = f"""
    <div class="leaderboard-card">
        <div class="category-title">{title}</div>
        <div class="top-rank-hero">
            <div class="gold-badge">1</div>
            <div class="hero-avatar-wrapper">
                <img class="hero-avatar" src="{top1_info['pfp']}" onerror="this.src='{default_pfp}';"/>
            </div>
            <div class="hero-name" title="{top1_info['name']}">{top1_info['name']}</div>
            <div class="hero-score">{top1_val_str}{unit}</div>
        </div>
        <div class="rank-list">
            {sub_rows_html}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# 헤더 렌더링
st.markdown("""
<div class="header-box">
    <h1>🏆 SSHS 기상곡 명예의 전당</h1>
    <p>실시간 기상곡 투표 현황 및 부문별 개인 랭킹 리더보드</p>
</div>
""", unsafe_allow_html=True)

# 3열 2행 카드 그리드 구성
col1, col2, col3 = st.columns(3)

with col1:
    render_card("❤️ 최다 좋아요 (총합)", likes_df, 'agree', '개')
    render_card("🎉 최다 기상곡 승인", app_df, 'approved_cnt', '곡')

with col2:
    render_card("💔 최다 싫어요 (총합)", dislikes_df, 'disagree', '개')
    render_card("🥇 최다 주별 1위", first_df, 'first_cnt', '회')

with col3:
    render_card("🔥 최다 순합산 (좋아요-싫어요)", net_df, 'net_votes', '점')
    render_card("📉 최다 주별 꼴등", last_df, 'last_cnt', '회')
