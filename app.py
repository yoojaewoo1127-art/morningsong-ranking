import streamlit as st
import requests
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="SSHS 기상곡 리더보드 & 전교생 통계",
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

    .section-header {
        font-size: 20px;
        font-weight: 800;
        color: #1e293b;
        margin: 30px 0 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로딩 및 전처리
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
            user_meta[int(sid)] = {"name": clean_name, "full_name": raw_name, "pfp": pfp}
            
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
        return {"name": "알 수 없음", "full_name": "알 수 없음", "pfp": default_pfp}
    return user_meta.get(int(pid), {"name": f"학생({int(pid)})", "full_name": f"학생({int(pid)})", "pfp": default_pfp})

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
        
        sub_items_html += f"<div class='sub-item'><div class='sub-left'><span class='sub-rank'>{rank_num}</span><img class='sub-avatar' src='{u_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/><span class='sub-name' title='{u_info['name']}'>{u_info['name']}</span></div><span class='sub-score'>{val_str}{unit}</span></div>"

    card_html = f"<div class='ranking-card'><div class='card-title'>{title}</div><div class='hero-section'><div class='gold-badge'>1</div><img class='hero-avatar' src='{top1_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/><div class='hero-name'>{top1_info['name']}</div><div class='{score_cls}'>{top1_val_str}{unit}</div></div><div class='sub-list'>{sub_items_html}</div></div>"
    
    st.markdown(card_html, unsafe_allow_html=True)

# 5. 상단 랭킹용 데이터 집계
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

# 6. 상단 UI 렌더링
st.markdown("""
<div class="main-title">
    <h1>🏆 SSHS 기상곡 명예의 전당</h1>
    <p>실시간 부문별 리더보드 & 전교생 통계 차트</p>
</div>
""", unsafe_allow_html=True)

tab_honor, tab_dishonor = st.tabs(["🏅 명예 기록", "💀 불명예 기록"])

with tab_honor:
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_leaderboard_card("❤️ 최다 좋아요", likes_df, 'agree', '개')
    with c2: render_leaderboard_card("🔥 최고 순합산 (Net)", net_high_df, 'net_votes', '점')
    with c3: render_leaderboard_card("🎉 최다 곡 승인", app_df, 'app_cnt', '곡')
    with c4: render_leaderboard_card("🥇 주별 1위 최다", first_cnt_df, 'first_cnt', '회')

with tab_dishonor:
    d1, d2, d3, d4 = st.columns(4)
    with d1: render_leaderboard_card("💔 최다 싫어요", dislikes_df, 'disagree', '개', is_danger=True)
    with d2: render_leaderboard_card("❄️ 최저 순합산 (Net)", net_low_df, 'net_votes', '점', is_danger=True)
    with d3: render_leaderboard_card("📉 주별 꼴등 최다", last_cnt_df, 'last_cnt', '회', is_danger=True)
    with d4: render_leaderboard_card("🚫 최다 승인 탈락", rej_df, 'rej_cnt', '곡', is_danger=True)

# -------------------------------------------------------------
# 7. 📊 전교생 종합 기록 차트 (선수 기록 스타일 정렬 테이블)
# -------------------------------------------------------------
st.markdown("<div class='section-header'>📋 전교생 종합 통계 기록실</div>", unsafe_allow_html=True)

# 1위 횟수 및 꼴등 횟수 매핑
first_map = first_cnt_df.set_index('proposer')['first_cnt'].to_dict()
last_map = last_cnt_df.set_index('proposer')['last_cnt'].to_dict()

# 학생별 전체 집계 데이터 생성
stat_records = []
grouped = df_songs.groupby('proposer')

for pid, group in grouped:
    u = get_user(pid)
    total_songs = len(group)
    total_agree = int(group['agree'].sum())
    total_disagree = int(group['disagree'].sum())
    total_net = int(group['net_votes'].sum())
    
    avg_agree = round(float(group['agree'].mean()), 2)
    avg_disagree = round(float(group['disagree'].mean()), 2)
    avg_net = round(float(group['net_votes'].mean()), 2)
    
    approved_count = int((group['approved'] == True).sum())
    approval_rate = round((approved_count / total_songs) * 100, 1)
    
    first_cnt = first_map.get(pid, 0)
    last_cnt = last_map.get(pid, 0)
    
    stat_records.append({
        "프로필": u['pfp'],
        "이름": u['name'],
        "교번": int(pid) if not pd.isna(pid) else 0,
        "곡 등록수": total_songs,
        "선정(승인)수": approved_count,
        "승인 성공률(%)": approval_rate,
        "순합산": total_net,
        "합산 좋아요": total_agree,
        "합산 싫어요": total_disagree,
        "평균 순합산": avg_net,
        "평균 좋아요": avg_agree,
        "평균 싫어요": avg_disagree,
        "주별 1등 횟수": first_cnt,
        "주별 꼴등 횟수": last_cnt
    })

df_all_stats = pd.DataFrame(stat_records)

# 기본 정렬: 순합산 높은 순
df_all_stats = df_all_stats.sort_values(by="순합산", ascending=False).reset_index(drop=True)

# 인터랙티브 정렬 테이블 렌더링
st.dataframe(
    df_all_stats,
    column_config={
        "프로필": st.column_config.ImageColumn("프로필", width="small"),
        "교번": st.column_config.NumberColumn("교번", format="%d"),
        "곡 등록수": st.column_config.NumberColumn("곡 등록수", help="신청한 총 곡 수"),
        "선정(승인)수": st.column_config.NumberColumn("선정 수", help="기상곡으로 최종 승인된 곡 수"),
        "승인 성공률(%)": st.column_config.ProgressColumn(
            "승인율",
            help="신청 곡 대비 승인 비율",
            format="%.1f%%",
            min_value=0,
            max_value=100
        ),
        "순합산": st.column_config.NumberColumn("순합산 (Net)"),
        "합산 좋아요": st.column_config.NumberColumn("합산 좋아요"),
        "합산 싫어요": st.column_config.NumberColumn("합산 싫어요"),
        "평균 순합산": st.column_config.NumberColumn("평균 Net", format="%.2f"),
        "평균 좋아요": st.column_config.NumberColumn("평균 좋아요", format="%.2f"),
        "평균 싫어요": st.column_config.NumberColumn("평균 싫어요", format="%.2f"),
        "주별 1등 횟수": st.column_config.NumberColumn("1등 횟수"),
        "주별 꼴등 횟수": st.column_config.NumberColumn("꼴등 횟수")
    },
    use_container_width=True,
    hide_index=False
)
