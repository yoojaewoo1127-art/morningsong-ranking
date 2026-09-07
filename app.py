import streamlit as st
import requests
import pandas as pd
import numpy as np
import math
import json

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="SSHS 기상곡 명예의 전당 & 개인 기록실",
    page_icon="🎵",
    layout="wide"
)

# URL 쿼리 파라미터 안전 조회
def get_query_param(key):
    try:
        if hasattr(st, "query_params") and key in st.query_params:
            val = st.query_params[key]
            return val[0] if isinstance(val, list) else val
    except Exception:
        pass
    try:
        params = st.experimental_get_query_params()
        if key in params and len(params[key]) > 0:
            return params[key][0]
    except Exception:
        pass
    return None

# 2. 커스텀 CSS (밑줄 제거 및 호버 시에만 밑줄 표시)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html {
        scroll-behavior: smooth;
    }

    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #f4f6f9;
    }

    /* Streamlit 기본 링크 파란 밑줄 원천 무효화 */
    .stApp a, .stApp a:link, .stApp a:visited {
        text-decoration: none !important;
        color: inherit !important;
    }

    .main-title {
        text-align: center;
        padding: 10px 0 16px 0;
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
        padding: 18px 14px 14px 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
        display: flex;
        flex-direction: column;
    }

    .card-title {
        font-size: 14px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .hero-section {
        text-align: center;
        padding-bottom: 12px;
        border-bottom: 1px solid #f1f5f9;
        position: relative;
    }

    .gold-badge {
        position: absolute;
        top: 0px;
        left: 4px;
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #ffffff;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        font-size: 12px;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 5px rgba(217, 119, 6, 0.3);
    }

    .hero-avatar {
        width: 68px;
        height: 68px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #f8fafc;
        box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        margin-bottom: 6px;
        transition: transform 0.15s ease;
    }

    .hero-name {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
        text-decoration: none !important;
        transition: color 0.15s ease;
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

    /* 2위 이하 리스트 (스크롤바) */
    .sub-list {
        margin-top: 8px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        max-height: 210px;
        overflow-y: auto;
        padding-right: 4px;
    }

    .sub-list::-webkit-scrollbar {
        width: 4px;
    }
    .sub-list::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }

    .sub-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 2px;
    }

    .sub-rank {
        font-size: 12.5px;
        font-weight: 700;
        color: #94a3b8 !important;
        width: 22px;
        text-align: center;
        flex-shrink: 0;
        text-decoration: none !important;
    }

    .sub-user-link {
        display: flex;
        align-items: center;
        gap: 8px;
        overflow: hidden;
        text-decoration: none !important;
        color: inherit !important;
        cursor: pointer;
        flex-grow: 1;
    }

    .sub-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid #e2e8f0;
        flex-shrink: 0;
        transition: transform 0.15s ease;
    }

    .sub-name {
        font-size: 12.5px;
        font-weight: 600;
        color: #334155 !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 85px;
        text-decoration: none !important;
        transition: color 0.15s ease;
    }

    .sub-score {
        font-size: 12.5px;
        font-weight: 700;
        color: #1e293b;
        flex-shrink: 0;
    }

    /* 커서 호버 시에만 파란색 밑줄 적용 */
    .hero-link {
        text-decoration: none !important;
        color: inherit !important;
        display: inline-block;
        cursor: pointer;
    }
    .hero-link:hover .hero-name,
    .sub-user-link:hover .sub-name {
        color: #2563eb !important;
        text-decoration: underline !important;
    }
    .hero-link:hover .hero-avatar,
    .sub-user-link:hover .sub-avatar {
        transform: scale(1.08);
    }

    .section-header {
        font-size: 20px;
        font-weight: 800;
        color: #1e293b;
        margin: 24px 0 12px 0;
    }

    /* 선수 상세 기록 카드 UI */
    .player-card {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .player-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 18px;
    }

    .player-avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #e2e8f0;
    }

    .player-title-box h3 {
        margin: 0;
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
    }

    .player-title-box p {
        margin: 2px 0 0 0;
        font-size: 13px;
        color: #64748b;
    }

    .ranking-badge-bar {
        background: #0f172a;
        color: #ffffff;
        border-radius: 10px;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 20px;
        font-size: 13.5px;
    }

    .badge-bar-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .badge-bar-item b {
        color: #fbbf24;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1px;
        background: #e2e8f0;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 20px;
    }

    .stats-cell {
        background: #ffffff;
        padding: 16px 10px;
        text-align: center;
    }

    .stats-cell-label {
        font-size: 12.5px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .stats-cell-val {
        font-size: 18px;
        font-weight: 800;
        color: #0f172a;
    }

    .stats-cell-val.highlight {
        color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로딩 및 전처리 (통계 제외 사유 태깅)
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
            sid_str = str(sid).strip()
            if sid_str.startswith("23"):
                continue
            
            raw_name = u.get("name", sid_str)
            clean_name = raw_name.split(" ")[-1] if " " in raw_name else raw_name
            pfp = u.get("pfp_url") if u.get("pfp_url") else default_pfp
            user_meta[int(sid)] = {"name": clean_name, "full_name": raw_name, "pfp": pfp}
            
    df_songs['proposer'] = pd.to_numeric(df_songs['proposer'], errors='coerce')
    df_songs = df_songs[~df_songs['proposer'].astype(str).str.startswith("23")].copy()
    
    df_songs['agree'] = pd.to_numeric(df_songs['agree'], errors='coerce').fillna(0).astype(int)
    df_songs['disagree'] = pd.to_numeric(df_songs['disagree'], errors='coerce').fillna(0).astype(int)
    df_songs['net_votes'] = df_songs['agree'] - df_songs['disagree']
    df_songs['approved'] = df_songs['approved'].apply(lambda x: True if str(x).lower() in ['true', '1'] else False)

    # 1) 방학 판별: 승인된 곡이 0건인 주차
    week_approved_cnt = df_songs.groupby(['year', 'week'])['approved'].transform(lambda x: (x == True).sum())
    is_vacation = (week_approved_cnt == 0)

    # 2) 밈/비음악 영상 판별: 방학이 아닌 정상 주차 중 상위 9위 이내이나 탈락한 곡
    df_songs['temp_week_rank'] = df_songs.groupby(['year', 'week'])['net_votes'].rank(ascending=False, method='min')
    is_meme = (~is_vacation) & (df_songs['temp_week_rank'] <= 9) & (df_songs['approved'] != True)

    def tag_reason(row):
        if is_vacation[row.name]:
            return "방학"
        elif is_meme[row.name]:
            return "노래 아님"
        return None

    df_songs['exclude_reason'] = df_songs.apply(tag_reason, axis=1)
    df_songs['is_excluded'] = df_songs['exclude_reason'].notna()
    df_songs.drop(columns=['temp_week_rank'], inplace=True, errors='ignore')

    return df_songs, user_meta, default_pfp

try:
    df_all_songs, user_meta, default_pfp = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

def get_user(pid):
    if pd.isna(pid):
        return {"name": "알 수 없음", "full_name": "알 수 없음", "pfp": default_pfp}
    return user_meta.get(int(pid), {"name": f"학생({int(pid)})", "full_name": f"학생({int(pid)})", "pfp": default_pfp})

# 모든 공식 통계 및 랭킹 산출은 '정상 반영곡'만 사용
df_valid_songs = df_all_songs[~df_all_songs['is_excluded']].copy()

# 4. 주차별 환경 보정 및 평균 기준 종합 기여도 산출
week_stats = df_valid_songs.groupby(['year', 'week'])['net_votes'].agg(['mean', 'std']).reset_index()
week_stats.rename(columns={'mean': 'week_mean', 'std': 'week_std'}, inplace=True)
df_valid_songs = pd.merge(df_valid_songs, week_stats, on=['year', 'week'], how='left')
df_valid_songs['week_std'] = df_valid_songs['week_std'].fillna(0)

df_valid_songs['z_week'] = np.where(
    df_valid_songs['week_std'] > 0,
    (df_valid_songs['net_votes'] - df_valid_songs['week_mean']) / df_valid_songs['week_std'],
    0.0
)

def norm_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

df_valid_songs['ev'] = 0.60 * (df_valid_songs['approved'] == True).astype(float) + 0.40 * df_valid_songs['z_week'].apply(norm_cdf)
mean_ev = float(df_valid_songs['ev'].mean()) if len(df_valid_songs) > 0 else 0.0
df_valid_songs['delta_ev'] = df_valid_songs['ev'] - mean_ev

student_score_map = df_valid_songs.groupby('proposer')['delta_ev'].sum().round(2).to_dict()

# 5. 1위 / 꼴등 횟수 계산
top_weekly = df_valid_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, False]).groupby(['year', 'week']).first().reset_index()
first_cnt_df = top_weekly.groupby('proposer').size().reset_index(name='first_cnt').sort_values(by='first_cnt', ascending=False).reset_index(drop=True)

bot_weekly = df_valid_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, True]).groupby(['year', 'week']).first().reset_index()
last_cnt_df = bot_weekly.groupby('proposer').size().reset_index(name='last_cnt').sort_values(by='last_cnt', ascending=False).reset_index(drop=True)

first_map = first_cnt_df.set_index('proposer')['first_cnt'].to_dict()
last_map = last_cnt_df.set_index('proposer')['last_cnt'].to_dict()

# 6. 전교생 기본 지표 집계
stat_records = []
grouped = df_valid_songs.groupby('proposer')

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
    score = student_score_map.get(pid, 0.0)
    
    stat_records.append({
        "pfp": u['pfp'],
        "name": u['name'],
        "student_id": int(pid) if not pd.isna(pid) else 0,
        "proposer": pid,
        "total_songs": total_songs,
        "approved_cnt": approved_count,
        "approval_rate": approval_rate,
        "total_net": total_net,
        "total_agree": total_agree,
        "total_disagree": total_disagree,
        "avg_net": avg_net,
        "avg_agree": avg_agree,
        "avg_disagree": avg_disagree,
        "first_cnt": first_cnt,
        "last_cnt": last_cnt,
        "score": score,
        "is_qualified": 1 if total_songs >= 4 else 0
    })

df_base_stat = pd.DataFrame(stat_records)

# 7. 상단 랭킹 데이터 집계
score_rank_df = df_base_stat[df_base_stat['is_qualified'] == 1].sort_values(by='score', ascending=False).reset_index(drop=True)
likes_df = df_valid_songs.groupby('proposer')['agree'].sum().reset_index().sort_values(by='agree', ascending=False).reset_index(drop=True)
net_high_df = df_valid_songs.groupby('proposer')['net_votes'].sum().reset_index().sort_values(by='net_votes', ascending=False).reset_index(drop=True)
app_df = df_valid_songs[df_valid_songs['approved'] == True].groupby('proposer').size().reset_index(name='app_cnt').sort_values(by='app_cnt', ascending=False).reset_index(drop=True)

dislikes_df = df_valid_songs.groupby('proposer')['disagree'].sum().reset_index().sort_values(by='disagree', ascending=False).reset_index(drop=True)
net_low_df = df_valid_songs.groupby('proposer')['net_votes'].sum().reset_index().sort_values(by='net_votes', ascending=True).reset_index(drop=True)
rej_df = df_valid_songs[df_valid_songs['approved'] == False].groupby('proposer').size().reset_index(name='rej_cnt').sort_values(by='rej_cnt', ascending=False).reset_index(drop=True)

# 8. 상단 카드 렌더링 함수
def render_leaderboard_card(title, df_rank, val_col, unit="", is_danger=False):
    if df_rank.empty:
        st.markdown(f"<div class='ranking-card'><div class='card-title'>{title}</div><p style='color:#94a3b8;'>기록 없음</p></div>", unsafe_allow_html=True)
        return

    top1 = df_rank.iloc[0]
    top1_id = int(top1['proposer']) if not pd.isna(top1['proposer']) else 0
    top1_info = get_user(top1_id)
    top1_val = top1[val_col]
    
    if unit == "점":
        top1_val_str = f"+{top1_val}" if top1_val > 0 else f"{top1_val}"
    elif unit == "":
        top1_val_str = f"+{top1_val:.2f}" if top1_val > 0 else f"{top1_val:.2f}"
    else:
        top1_val_str = f"{top1_val}"
        
    score_cls = "hero-score danger" if is_danger else "hero-score"

    sub_items_html = ""
    for rank_num, row in enumerate(df_rank.iloc[1:15].itertuples(), start=2):
        pid_raw = getattr(row, 'proposer')
        pid = int(pid_raw) if not pd.isna(pid_raw) else 0
        u_info = get_user(pid)
        val = getattr(row, val_col)
        
        if unit == "":
            val_str = f"+{val:.2f}" if val > 0 else f"{val:.2f}"
        elif unit == "점" and val > 0:
            val_str = f"+{val}"
        else:
            val_str = f"{val}"
            
        sub_items_html += f"""
        <div class='sub-item'>
            <span class='sub-rank'>{rank_num}</span>
            <a href='/?student={pid}' target='_top' class='sub-user-link' title='{u_info['name']} 학생 정보 조회'>
                <img class='sub-avatar' src='{u_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/>
                <span class='sub-name'>{u_info['name']}</span>
            </a>
            <span class='sub-score'>{val_str}{unit}</span>
        </div>
        """

    card_html = f"""
    <div class='ranking-card'>
        <div class='card-title'>{title}</div>
        <div class='hero-section'>
            <div class='gold-badge'>1</div>
            <a href='/?student={top1_id}' target='_top' class='hero-link' title='{top1_info['name']} 학생 정보 조회'>
                <img class='hero-avatar' src='{top1_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/>
                <div class='hero-name'>{top1_info['name']}</div>
            </a>
            <div class='{score_cls}'>{top1_val_str}{unit}</div>
        </div>
        <div class='sub-list'>{sub_items_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# 9. 상단 리더보드 UI
st.markdown("""
<div class="main-title">
    <h1>🏆 SSHS 기상곡 명예의 전당</h1>
    <p>실시간 부문별 리더보드 & 전교생 개인 기록실</p>
</div>
""", unsafe_allow_html=True)

tab_honor, tab_dishonor = st.tabs(["🏅 명예 기록", "💀 불명예 기록"])

with tab_honor:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: render_leaderboard_card("👑 종합 기여도", score_rank_df, 'score', '')
    with c2: render_leaderboard_card("🔥 최고 순합산 (Net)", net_high_df, 'net_votes', '점')
    with c3: render_leaderboard_card("🎉 최다 곡 승인", app_df, 'app_cnt', '곡')
    with c4: render_leaderboard_card("🥇 주별 1위 최다", first_cnt_df, 'first_cnt', '회')
    with c5: render_leaderboard_card("❤️ 최다 좋아요", likes_df, 'agree', '개')

with tab_dishonor:
    d1, d2, d3, d4 = st.columns(4)
    with d1: render_leaderboard_card("💔 최다 싫어요", dislikes_df, 'disagree', '개', is_danger=True)
    with d2: render_leaderboard_card("❄️ 최저 순합산 (Net)", net_low_df, 'net_votes', '점', is_danger=True)
    with d3: render_leaderboard_card("📉 주별 꼴등 최다", last_cnt_df, 'last_cnt', '회', is_danger=True)
    with d4: render_leaderboard_card("🚫 최다 승인 탈락", rej_df, 'rej_cnt', '곡', is_danger=True)

# -------------------------------------------------------------
# 10. 🔍 선수(학생) 개별 기록 검색 및 상세 리포트 카드
# -------------------------------------------------------------
st.markdown("<div id='player-section' class='section-header'>🔍 학생 개인별 상세 기록 조회</div>", unsafe_allow_html=True)

all_proposers = df_all_songs['proposer'].dropna().unique().astype(int)
user_options = []
user_id_map = {}
user_id_to_label = {}

for pid in all_proposers:
    u = get_user(pid)
    label = f"{u['name']} ({pid})"
    user_options.append(label)
    user_id_map[label] = pid
    user_id_to_label[pid] = label

user_options.sort()
all_options = ["선택 안 함"] + user_options

# URL 파라미터 연동: 세션 스테이트 동기화
param_student = get_query_param("student")
if param_student:
    try:
        p_id = int(param_student)
        if p_id in user_id_to_label:
            st.session_state["student_search_box"] = user_id_to_label[p_id]
    except Exception:
        pass

selected_label = st.selectbox(
    "이름 또는 교번을 검색하세요 (위 리더보드나 아래 순위표에서 이름을 클릭해도 바로 조회됩니다):",
    options=all_options,
    key="student_search_box"
)

if selected_label != "선택 안 함":
    target_pid = user_id_map[selected_label]
    target_u = get_user(target_pid)
    
    user_all = df_all_songs[df_all_songs['proposer'] == target_pid].copy()
    user_valid = user_all[~user_all['is_excluded']].copy()
    user_excluded = user_all[user_all['is_excluded']].copy()
    
    p_total_songs = len(user_valid)
    p_approved = int((user_valid['approved'] == True).sum())
    p_rate = round((p_approved / p_total_songs) * 100, 1) if p_total_songs > 0 else 0.0
    p_net = int(user_valid['net_votes'].sum())
    p_agree = int(user_valid['agree'].sum())
    p_disagree = int(user_valid['disagree'].sum())
    p_avg_net = round(float(user_valid['net_votes'].mean()), 2) if p_total_songs > 0 else 0.0
    p_avg_agree = round(float(user_valid['agree'].mean()), 2) if p_total_songs > 0 else 0.0
    p_avg_disagree = round(float(user_valid['disagree'].mean()), 2) if p_total_songs > 0 else 0.0
    
    row_stat = df_base_stat[df_base_stat['student_id'] == target_pid]
    p_score = row_stat['score'].iloc[0] if not row_stat.empty else 0.0
    
    def get_rank_str(df_rank, val_col):
        res = df_rank[df_rank['proposer'] == target_pid]
        if not res.empty:
            r = res.index[0] + 1
            return f"<b>{r}위</b>"
        return "순위 밖"

    r_score = get_rank_str(score_rank_df, 'score')
    r_net = get_rank_str(net_high_df, 'net_votes')
    r_agree = get_rank_str(likes_df, 'agree')
    r_app = get_rank_str(app_df, 'app_cnt')

    score_display_str = f"+{p_score:.2f}" if p_score > 0 else f"{p_score:.2f}"

    st.markdown(f"""
    <div class="player-card">
        <div class="player-header">
            <img class="player-avatar" src="{target_u['pfp']}" onerror="this.src='{default_pfp}'"/>
            <div class="player-title-box">
                <h3>{target_u['name']} <span style="font-size: 14px; font-weight: normal; color: #64748b;">(교번: {target_pid})</span></h3>
                <p>SSHS 기상곡 아티스트</p>
            </div>
        </div>
        <div class="ranking-badge-bar">
            <span>🏆 <b>공식 랭킹</b></span>
            <span class="badge-bar-item">종합 점수 {r_score}</span> ·
            <span class="badge-bar-item">순합산 {r_net}</span> ·
            <span class="badge-bar-item">좋아요 {r_agree}</span> ·
            <span class="badge-bar-item">선정 곡수 {r_app}</span>
        </div>
        <div class="stats-grid">
            <div class="stats-cell">
                <div class="stats-cell-label">종합 기여도 점수</div>
                <div class="stats-cell-val highlight">{score_display_str}</div>
            </div>
            <div class="stats-cell">
                <div class="stats-cell-label">순합산 (Net)</div>
                <div class="stats-cell-val">{'+' + str(p_net) if p_net > 0 else p_net}점</div>
            </div>
            <div class="stats-cell">
                <div class="stats-cell-label">승인율 (성공/등록)</div>
                <div class="stats-cell-val">{p_rate}% <span style="font-size:13px; color:#64748b;">({p_approved}/{p_total_songs})</span></div>
            </div>
            <div class="stats-cell">
                <div class="stats-cell-label">최종 승인 곡수</div>
                <div class="stats-cell-val highlight">{p_approved}곡</div>
            </div>
            <div class="stats-cell">
                <div class="stats-cell-label">합산 좋아요</div>
                <div class="stats-cell-val">{p_agree}개</div>
            </div>
            <div class="stats-cell">
                <div class="stats-cell-label">합산 싫어요</div>
                <div class="stats-cell-val">{p_disagree}개</div>
            </div>
            <div class="stats-cell">
                <div class="stats-cell-label">곡당 평균 Net</div>
                <div class="stats-cell-val">{'+' + str(p_avg_net) if p_avg_net > 0 else p_avg_net}</div>
            </div>
            <div class="stats-cell">
                <div class="stats-cell-label">곡당 평균 좋아요</div>
                <div class="stats-cell-val">{p_avg_agree}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 📈 주차별 신청곡 득표 추이 그래프
    if len(user_valid) > 0:
        valid_sorted = user_valid.sort_values(by=['year', 'week'], ascending=[True, True]).copy()
        valid_sorted['주차'] = valid_sorted['year'].astype(str) + "년 " + valid_sorted['week'].astype(str) + "주"
        chart_data = valid_sorted[['주차', 'net_votes', 'agree', 'disagree']].rename(columns={
            'net_votes': '순합산(Net)',
            'agree': '좋아요',
            'disagree': '싫어요'
        }).set_index('주차')
        st.caption("📈 주차별 유효 신청곡 득표 추이")
        st.line_chart(chart_data)

    # 🎵 정상 반영된 신청 기상곡 목록
    st.markdown(f"<div style='font-size: 16px; font-weight: 700; color: #1e293b; margin: 20px 0 8px 0;'>🎵 정상 반영된 신청곡 목록 ({len(user_valid)}곡)</div>", unsafe_allow_html=True)
    
    if len(user_valid) > 0:
        valid_table = user_valid.sort_values(by=['year', 'week'], ascending=[False, False]).copy()
        valid_items = []
        for _, s in valid_table.iterrows():
            valid_items.append({
                "week": f"{s['year']}년 {s['week']}주",
                "title": str(s.get('title', '제목 없음')),
                "net": int(s.get('net_votes', 0)),
                "agree": int(s.get('agree', 0)),
                "disagree": int(s.get('disagree', 0)),
                "approved": bool(s.get('approved', False))
            })
        valid_items_json = json.dumps(valid_items)
        v_height = min(360, max(160, 60 + len(valid_items) * 44))

        st.components.v1.html(f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            * {{ box-sizing: border-box; font-family: 'Pretendard', sans-serif; }}
            body {{ margin: 0; padding: 0; background: transparent; }}
            .song-card {{ background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; position: relative; }}
            .top-scroll {{ position: sticky; top: 0; z-index: 50; overflow-x: auto; background: #f1f5f9; height: 10px; }}
            .top-scroll::-webkit-scrollbar {{ height: 8px; }}
            .top-scroll::-webkit-scrollbar-thumb {{ background: #3b82f6; border-radius: 4px; }}
            .tbl-wrap {{ overflow-x: auto; max-height: 300px; overflow-y: auto; width: 100%; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; white-space: nowrap; }}
            th {{ position: sticky; top: 0; z-index: 40; background: #f8fafc; color: #64748b; font-weight: 700; padding: 10px 14px; border-bottom: 2px solid #e2e8f0; text-align: right; }}
            th:first-child, th:nth-child(2) {{ text-align: left; }}
            td {{ padding: 10px 14px; border-bottom: 1px solid #f1f5f9; color: #1e293b; text-align: right; }}
            td:first-child, td:nth-child(2) {{ text-align: left; }}
            tr:hover td {{ background-color: #f8fafc; }}
            .badge-app {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 700; background: #dcfce7; color: #166534; }}
            .badge-rej {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 600; background: #fee2e2; color: #991b1b; }}
        </style>
        </head>
        <body>
        <div class="song-card">
            <div id="vTop" class="top-scroll"><div id="vTopInner" style="height:1px;"></div></div>
            <div id="vBot" class="tbl-wrap">
                <table id="vTable">
                    <thead><tr><th>신청 주차</th><th>곡 제목</th><th>순합산 (Net)</th><th>좋아요</th><th>싫어요</th><th style="text-align:center;">선정 결과</th></tr></thead>
                    <tbody id="vBody"></tbody>
                </table>
            </div>
        </div>
        <script>
            const data = {valid_items_json};
            const tbody = document.getElementById('vBody');
            data.forEach(s => {{
                const tr = document.createElement('tr');
                const netStr = s.net > 0 ? '+' + s.net : s.net;
                const badge = s.approved ? "<span class='badge-app'>✅ 최종 승인</span>" : "<span class='badge-rej'>❌ 탈락</span>";
                tr.innerHTML = `<td>${{s.week}}</td><td style="font-weight:600;">${{s.title}}</td><td style="font-weight:700;color:#2563eb;">${{netStr}}</td><td>${{s.agree}}</td><td>${{s.disagree}}</td><td style="text-align:center;">${{badge}}</td>`;
                tbody.appendChild(tr);
            }});
            const topEl = document.getElementById('vTop');
            const botEl = document.getElementById('vBot');
            const innerEl = document.getElementById('vTopInner');
            const tbl = document.getElementById('vTable');
            function sync() {{ innerEl.style.width = tbl.scrollWidth + 'px'; }}
            setTimeout(sync, 40);
            window.addEventListener('resize', sync);
            let sTop = false, sBot = false;
            topEl.addEventListener('scroll', () => {{ if(!sTop) {{ sBot = true; botEl.scrollLeft = topEl.scrollLeft; }} sTop = false; }});
            botEl.addEventListener('scroll', () => {{ if(!sBot) {{ sTop = true; topEl.scrollLeft = botEl.scrollLeft; }} sBot = false; }});
        </script>
        </body>
        </html>
        """, height=v_height, scrolling=False)
    else:
        st.info("정상 반영된 신청곡이 없습니다.")

    # ⚠️ 통계에서 제외된 신청 기상곡 목록
    st.markdown(f"<div style='font-size: 16px; font-weight: 700; color: #dc2626; margin: 24px 0 8px 0;'>⚠️ 통계에서 제외된 신청곡 목록 ({len(user_excluded)}곡)</div>", unsafe_allow_html=True)
    
    if len(user_excluded) > 0:
        ex_table = user_excluded.sort_values(by=['year', 'week'], ascending=[False, False]).copy()
        ex_items = []
        for _, s in ex_table.iterrows():
            ex_items.append({
                "week": f"{s['year']}년 {s['week']}주",
                "title": str(s.get('title', '제목 없음')),
                "net": int(s.get('net_votes', 0)),
                "agree": int(s.get('agree', 0)),
                "disagree": int(s.get('disagree', 0)),
                "reason": str(s.get('exclude_reason', '기타 제외'))
            })
        ex_items_json = json.dumps(ex_items)
        e_height = min(320, max(150, 60 + len(ex_items) * 44))

        st.components.v1.html(f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            * {{ box-sizing: border-box; font-family: 'Pretendard', sans-serif; }}
            body {{ margin: 0; padding: 0; background: transparent; }}
            .song-card {{ background: #fff; border-radius: 12px; border: 1px solid #fed7aa; position: relative; }}
            .top-scroll {{ position: sticky; top: 0; z-index: 50; overflow-x: auto; background: #fff7ed; height: 10px; }}
            .top-scroll::-webkit-scrollbar {{ height: 8px; }}
            .top-scroll::-webkit-scrollbar-thumb {{ background: #f97316; border-radius: 4px; }}
            .tbl-wrap {{ overflow-x: auto; max-height: 260px; overflow-y: auto; width: 100%; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; white-space: nowrap; }}
            th {{ position: sticky; top: 0; z-index: 40; background: #fff7ed; color: #9a3412; font-weight: 700; padding: 10px 14px; border-bottom: 2px solid #fed7aa; text-align: right; }}
            th:first-child, th:nth-child(2) {{ text-align: left; }}
            td {{ padding: 10px 14px; border-bottom: 1px solid #ffedd5; color: #1e293b; text-align: right; }}
            td:first-child, td:nth-child(2) {{ text-align: left; }}
            tr:hover td {{ background-color: #fffaf5; }}
            .badge-meme {{ display: inline-block; padding: 3px 8px; border-radius: 10px; font-size: 12px; font-weight: 700; background: #fee2e2; color: #b91c1c; }}
            .badge-vac {{ display: inline-block; padding: 3px 8px; border-radius: 10px; font-size: 12px; font-weight: 700; background: #e0f2fe; color: #0369a1; }}
        </style>
        </head>
        <body>
        <div class="song-card">
            <div id="eTop" class="top-scroll"><div id="eTopInner" style="height:1px;"></div></div>
            <div id="eBot" class="tbl-wrap">
                <table id="eTable">
                    <thead><tr><th>신청 주차</th><th>곡 제목</th><th>순합산 (Net)</th><th>좋아요</th><th>싫어요</th><th style="text-align:center;">제외 사유</th></tr></thead>
                    <tbody id="eBody"></tbody>
                </table>
            </div>
        </div>
        <script>
            const data = {ex_items_json};
            const tbody = document.getElementById('eBody');
            data.forEach(s => {{
                const tr = document.createElement('tr');
                const netStr = s.net > 0 ? '+' + s.net : s.net;
                const badge = s.reason === '노래 아님' 
                    ? "<span class='badge-meme'>🚫 노래 아님</span>" 
                    : "<span class='badge-vac'>🏖️ 방학</span>";
                tr.innerHTML = `<td>${{s.week}}</td><td style="font-weight:600; color:#475569;">${{s.title}}</td><td>${{netStr}}</td><td>${{s.agree}}</td><td>${{s.disagree}}</td><td style="text-align:center;">${{badge}}</td>`;
                tbody.appendChild(tr);
            }});
            const topEl = document.getElementById('eTop');
            const botEl = document.getElementById('eBot');
            const innerEl = document.getElementById('eTopInner');
            const tbl = document.getElementById('eTable');
            function sync() {{ innerEl.style.width = tbl.scrollWidth + 'px'; }}
            setTimeout(sync, 40);
            window.addEventListener('resize', sync);
            let sTop = false, sBot = false;
            topEl.addEventListener('scroll', () => {{ if(!sTop) {{ sBot = true; botEl.scrollLeft = topEl.scrollLeft; }} sTop = false; }});
            botEl.addEventListener('scroll', () => {{ if(!sBot) {{ sTop = true; topEl.scrollLeft = botEl.scrollLeft; }} sBot = false; }});
        </script>
        </body>
        </html>
        """, height=e_height, scrolling=False)
    else:
        st.success("통계에서 제외된 곡이 없습니다. (모든 신청곡이 정상 반영되었습니다)")

# -------------------------------------------------------------
# 11. 📊 전교생 종합 기록실 (이름 클릭 시 정보창 연동)
# -------------------------------------------------------------
st.markdown("<div class='section-header'>📋 전교생 종합 통계 기록실 <span style='font-size: 13px; font-weight: normal; color: #64748b;'>(※ 이름을 클릭하면 상단에서 상세 기록과 제외곡을 즉시 확인할 수 있습니다)</span></div>", unsafe_allow_html=True)

table_data_json = json.dumps(df_base_stat.to_dict(orient='records'))

html_table_component = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {{ box-sizing: border-box; font-family: 'Pretendard', sans-serif; }}
    body {{ margin: 0; padding: 0; background-color: transparent; }}
    .table-card {{ background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04); position: relative; }}
    .top-scrollbar-wrapper {{ position: sticky; top: 0; z-index: 50; overflow-x: auto; background: #f1f5f9; border-bottom: 2px solid #cbd5e1; height: 12px; }}
    .top-scrollbar-wrapper::-webkit-scrollbar {{ height: 10px; }}
    .top-scrollbar-wrapper::-webkit-scrollbar-thumb {{ background: #3b82f6; border-radius: 5px; }}
    .table-scroll-container {{ overflow-x: auto; width: 100%; max-height: 700px; overflow-y: auto; }}
    table {{ width: 100%; border-collapse: collapse; text-align: right; font-size: 13.5px; white-space: nowrap; }}
    thead th {{ position: sticky; top: 0; z-index: 40; background: #f8fafc; color: #64748b; font-weight: 700; padding: 12px 10px; border-bottom: 2px solid #e2e8f0; cursor: pointer; user-select: none; }}
    thead th:hover {{ background: #eef2f6; color: #1e293b; }}
    thead th.active {{ color: #2563eb; }}
    .sort-arrow {{ display: inline-block; font-size: 10px; margin-left: 4px; opacity: 0.3; transition: transform 0.2s ease; }}
    .sort-arrow.desc {{ transform: rotate(180deg); }}
    tbody td {{ padding: 10px; border-bottom: 1px solid #f1f5f9; color: #1e293b; }}
    tbody tr:hover td {{ background-color: #f8fafc; }}
    .col-rank {{ text-align: center; font-weight: 700; color: #94a3b8; width: 45px; }}
    .col-rank.unqualified {{ color: #cbd5e1; font-size: 15px; }}
    
    /* 사용자 링크 밑줄 방지 및 호버 밑줄 */
    .col-user-link {{ text-align: left; display: flex; align-items: center; gap: 8px; text-decoration: none !important; color: inherit !important; cursor: pointer; }}
    .avatar {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1px solid #e2e8f0; transition: transform 0.15s ease; }}
    .user-name {{ font-weight: 600; color: #0f172a; text-decoration: none !important; transition: color 0.15s ease; }}
    .col-user-link:hover .user-name {{ color: #2563eb !important; text-decoration: underline !important; }}
    .col-user-link:hover .avatar {{ transform: scale(1.1); }}
    .highlight-cell {{ font-weight: 700; color: #2563eb; }}
</style>
</head>
<body>

<div class="table-card">
    <div id="topScrollWrapper" class="top-scrollbar-wrapper">
        <div id="topScrollContent" style="height: 1px;"></div>
    </div>
    
    <div id="tableScrollContainer" class="table-scroll-container">
        <table id="statsTable">
            <thead>
                <tr>
                    <th style="cursor: default; text-align: center;">순위</th>
                    <th onclick="sortTable('name')" style="text-align: left;">선수/이름 <span class="sort-arrow" id="arrow-name">▲</span></th>
                    <th onclick="sortTable('student_id')">교번 <span class="sort-arrow" id="arrow-student_id">▲</span></th>
                    <th onclick="sortTable('score')" class="active">종합 기여도 <span class="sort-arrow desc" id="arrow-score">▲</span></th>
                    <th onclick="sortTable('total_net')">순합산(Net) <span class="sort-arrow" id="arrow-total_net">▲</span></th>
                    <th onclick="sortTable('total_songs')">곡 등록수 <span class="sort-arrow" id="arrow-total_songs">▲</span></th>
                    <th onclick="sortTable('approved_cnt')">선정수 <span class="sort-arrow" id="arrow-approved_cnt">▲</span></th>
                    <th onclick="sortTable('approval_rate')">승인율 <span class="sort-arrow" id="arrow-approval_rate">▲</span></th>
                    <th onclick="sortTable('total_agree')">합산 좋아요 <span class="sort-arrow" id="arrow-total_agree">▲</span></th>
                    <th onclick="sortTable('total_disagree')">합산 싫어요 <span class="sort-arrow" id="arrow-total_disagree">▲</span></th>
                    <th onclick="sortTable('avg_net')">평균 Net <span class="sort-arrow" id="arrow-avg_net">▲</span></th>
                    <th onclick="sortTable('avg_agree')">평균 좋아요 <span class="sort-arrow" id="arrow-avg_agree">▲</span></th>
                    <th onclick="sortTable('avg_disagree')">평균 싫어요 <span class="sort-arrow" id="arrow-avg_disagree">▲</span></th>
                    <th onclick="sortTable('first_cnt')">1등 횟수 <span class="sort-arrow" id="arrow-first_cnt">▲</span></th>
                    <th onclick="sortTable('last_cnt')">꼴등 횟수 <span class="sort-arrow" id="arrow-last_cnt">▲</span></th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>
    </div>
</div>

<script>
    let rawData = {table_data_json};
    let currentKey = 'score';
    let isAsc = false;

    const topScroll = document.getElementById('topScrollWrapper');
    const bottomScroll = document.getElementById('tableScrollContainer');
    const topContent = document.getElementById('topScrollContent');
    const table = document.getElementById('statsTable');

    function syncWidth() {{
        if (table && topContent) {{
            topContent.style.width = table.scrollWidth + 'px';
        }}
    }}
    window.addEventListener('resize', syncWidth);

    let isSyncingTop = false;
    let isSyncingBottom = false;

    topScroll.addEventListener('scroll', () => {{
        if (!isSyncingTop) {{
            isSyncingBottom = true;
            bottomScroll.scrollLeft = topScroll.scrollLeft;
        }}
        isSyncingTop = false;
    }});

    bottomScroll.addEventListener('scroll', () => {{
        if (!isSyncingBottom) {{
            isSyncingTop = true;
            topScroll.scrollLeft = bottomScroll.scrollLeft;
        }}
        isSyncingBottom = false;
    }});

    function openStudent(id) {{
        window.top.location.href = '/?student=' + id;
    }}

    function renderTable(sortedData) {{
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        
        let rankCounter = 1;

        sortedData.forEach((row) => {{
            const tr = document.createElement('tr');
            
            let rankDisplay = "-";
            let rankClass = "col-rank unqualified";
            if (row.is_qualified === 1) {{
                rankDisplay = rankCounter;
                rankClass = "col-rank";
                rankCounter++;
            }}

            let scoreFormatted = row.score > 0 ? '+' + row.score.toFixed(2) : row.score.toFixed(2);

            tr.innerHTML = `
                <td class="${{rankClass}}">${{rankDisplay}}</td>
                <td>
                    <div onclick="openStudent('${{row.student_id}}')" class="col-user-link" title="${{row.name}} 학생 정보 조회">
                        <img class="avatar" src="${{row.pfp}}" onerror="this.src='{default_pfp}'"/>
                        <span class="user-name">${{row.name}}</span>
                    </div>
                </td>
                <td>${{row.student_id}}</td>
                <td class="highlight-cell">${{scoreFormatted}}</td>
                <td>${{row.total_net > 0 ? '+' + row.total_net : row.total_net}}</td>
                <td>${{row.total_songs}}</td>
                <td>${{row.approved_cnt}}</td>
                <td>${{row.approval_rate.toFixed(1)}}%</td>
                <td>${{row.total_agree}}</td>
                <td>${{row.total_disagree}}</td>
                <td>${{row.avg_net > 0 ? '+' + row.avg_net.toFixed(2) : row.avg_net.toFixed(2)}}</td>
                <td>${{row.avg_agree.toFixed(2)}}</td>
                <td>${{row.avg_disagree.toFixed(2)}}</td>
                <td>${{row.first_cnt}}</td>
                <td>${{row.last_cnt}}</td>
            `;
            tbody.appendChild(tr);
        }});

        setTimeout(syncWidth, 40);
    }}

    function doSort(key, asc) {{
        let qualified = rawData.filter(d => d.is_qualified === 1);
        let unqualified = rawData.filter(d => d.is_qualified === 0);

        const comparator = (a, b) => {{
            let valA = a[key];
            let valB = b[key];
            if (typeof valA === 'string') {{
                return asc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }}
            return asc ? valA - valB : valB - valA;
        }};

        qualified.sort(comparator);
        unqualified.sort(comparator);

        return qualified.concat(unqualified);
    }}

    function sortTable(key) {{
        if (currentKey === key) {{
            isAsc = !isAsc;
        }} else {{
            currentKey = key;
            isAsc = (key === 'name' || key === 'student_id') ? true : false;
        }}

        const sortedData = doSort(key, isAsc);

        document.querySelectorAll('th').forEach(th => th.classList.remove('active'));
        document.querySelectorAll('.sort-arrow').forEach(ar => {{
            ar.classList.remove('desc');
            ar.style.opacity = '0.3';
        }});

        const targetTh = event.currentTarget;
        targetTh.classList.add('active');
        const arrow = document.getElementById('arrow-' + key);
        if (arrow) {{
            arrow.style.opacity = '1';
            if (!isAsc) {{
                arrow.classList.add('desc');
            }}
        }}

        renderTable(sortedData);
    }}

    const initialData = doSort('score', false);
    renderTable(initialData);
</script>
</body>
</html>
"""

st.components.v1.html(html_table_component, height=760, scrolling=False)
