import streamlit as st
import requests
import pandas as pd
import json

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="SSHS 기상곡 명예의 전당 & 개인 기록실",
    page_icon="🎵",
    layout="wide"
)

# 2. 커스텀 CSS (스크롤바 및 카드 스타일)
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

    /* 2위 이하 리스트 (스크롤바 적용) */
    .sub-list {
        margin-top: 8px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        max-height: 210px;
        overflow-y: auto;
        padding-right: 4px;
    }

    /* 스크롤바 미세 디자인 */
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

    .sub-left {
        display: flex;
        align-items: center;
        gap: 8px;
        overflow: hidden;
    }

    .sub-rank {
        font-size: 12.5px;
        font-weight: 700;
        color: #94a3b8;
        width: 14px;
        text-align: center;
    }

    .sub-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid #e2e8f0;
        flex-shrink: 0;
    }

    .sub-name {
        font-size: 12.5px;
        font-weight: 600;
        color: #334155;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 80px;
    }

    .sub-score {
        font-size: 12.5px;
        font-weight: 700;
        color: #1e293b;
        flex-shrink: 0;
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
        margin-bottom: 24px;
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

# 3. 데이터 로딩 및 전처리 (23학번 졸업생 필터링)
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

# 4. 1위 / 꼴등 데이터 계산
top_weekly = df_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, False]).groupby(['year', 'week']).first().reset_index()
first_cnt_df = top_weekly.groupby('proposer').size().reset_index(name='first_cnt').sort_values(by='first_cnt', ascending=False).reset_index(drop=True)

bot_weekly = df_songs.sort_values(by=['year', 'week', 'net_votes'], ascending=[True, True, True]).groupby(['year', 'week']).first().reset_index()
last_cnt_df = bot_weekly.groupby('proposer').size().reset_index(name='last_cnt').sort_values(by='last_cnt', ascending=False).reset_index(drop=True)

first_map = first_cnt_df.set_index('proposer')['first_cnt'].to_dict()
last_map = last_cnt_df.set_index('proposer')['last_cnt'].to_dict()

# 5. 전교생 기본 지표 집계
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
        "is_qualified": 1 if total_songs >= 4 else 0
    })

df_base_stat = pd.DataFrame(stat_records)

# 6. Z-Score 기반 종합 기여도 점수 산출
def calc_z(series):
    std = series.std(ddof=0)
    return (series - series.mean()) / std if std > 0 else series * 0

df_base_stat['z_app'] = calc_z(df_base_stat['approved_cnt'])
df_base_stat['z_net'] = calc_z(df_base_stat['total_net'])
df_base_stat['z_first'] = calc_z(df_base_stat['first_cnt'])
df_base_stat['z_avg_net'] = calc_z(df_base_stat['avg_net'])
df_base_stat['z_last'] = calc_z(df_base_stat['last_cnt'])

df_base_stat['score'] = (
    0.35 * df_base_stat['z_app'] +
    0.30 * df_base_stat['z_net'] +
    0.20 * df_base_stat['z_first'] +
    0.15 * df_base_stat['z_avg_net'] -
    0.15 * df_base_stat['z_last']
).round(2)

# 7. 상단 랭킹 데이터 집계
score_rank_df = df_base_stat[df_base_stat['is_qualified'] == 1].sort_values(by='score', ascending=False).reset_index(drop=True)
likes_df = df_songs.groupby('proposer')['agree'].sum().reset_index().sort_values(by='agree', ascending=False).reset_index(drop=True)
net_high_df = df_songs.groupby('proposer')['net_votes'].sum().reset_index().sort_values(by='net_votes', ascending=False).reset_index(drop=True)
app_df = df_songs[df_songs['approved'] == True].groupby('proposer').size().reset_index(name='app_cnt').sort_values(by='app_cnt', ascending=False).reset_index(drop=True)

dislikes_df = df_songs.groupby('proposer')['disagree'].sum().reset_index().sort_values(by='disagree', ascending=False).reset_index(drop=True)
net_low_df = df_songs.groupby('proposer')['net_votes'].sum().reset_index().sort_values(by='net_votes', ascending=True).reset_index(drop=True)
rej_df = df_songs[df_songs['approved'] == False].groupby('proposer').size().reset_index(name='rej_cnt').sort_values(by='rej_cnt', ascending=False).reset_index(drop=True)

# 8. 상단 카드 렌더링 함수 (스크롤 지원: 최대 15위까지 렌더링)
def render_leaderboard_card(title, df_rank, val_col, unit="", is_danger=False):
    if df_rank.empty:
        st.markdown(f"<div class='ranking-card'><div class='card-title'>{title}</div><p style='color:#94a3b8;'>기록 없음</p></div>", unsafe_allow_html=True)
        return

    top1 = df_rank.iloc[0]
    top1_info = get_user(top1['proposer'])
    top1_val = top1[val_col]
    
    if unit == "점":
        top1_val_str = f"+{top1_val}" if top1_val > 0 else f"{top1_val}"
    elif unit == "":
        top1_val_str = f"+{top1_val:.2f}" if top1_val > 0 else f"{top1_val:.2f}"
    else:
        top1_val_str = f"{top1_val}"
        
    score_cls = "hero-score danger" if is_danger else "hero-score"

    # 2위부터 최대 15위까지 스크롤 리스트에 포함
    sub_items_html = ""
    for rank_num, row in enumerate(df_rank.iloc[1:15].itertuples(), start=2):
        u_info = get_user(getattr(row, 'proposer'))
        val = getattr(row, val_col)
        
        if unit == "":
            val_str = f"+{val:.2f}" if val > 0 else f"{val:.2f}"
        elif unit == "점" and val > 0:
            val_str = f"+{val}"
        else:
            val_str = f"{val}"
            
        sub_items_html += f"<div class='sub-item'><div class='sub-left'><span class='sub-rank'>{rank_num}</span><img class='sub-avatar' src='{u_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/><span class='sub-name' title='{u_info['name']}'>{u_info['name']}</span></div><span class='sub-score'>{val_str}{unit}</span></div>"

    card_html = f"<div class='ranking-card'><div class='card-title'>{title}</div><div class='hero-section'><div class='gold-badge'>1</div><img class='hero-avatar' src='{top1_info['pfp']}' onerror=\"this.src='{default_pfp}';\"/><div class='hero-name'>{top1_info['name']}</div><div class='{score_cls}'>{top1_val_str}{unit}</div></div><div class='sub-list'>{sub_items_html}</div></div>"
    st.markdown(card_html, unsafe_allow_html=True)

# 9. 상단 UI 렌더링
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
st.markdown("<div class='section-header'>🔍 학생 개인별 상세 기록 조회</div>", unsafe_allow_html=True)

all_proposers = df_songs['proposer'].dropna().unique().astype(int)
user_options = []
user_id_map = {}

for pid in all_proposers:
    u = get_user(pid)
    label = f"{u['name']} ({pid})"
    user_options.append(label)
    user_id_map[label] = pid

user_options.sort()

selected_label = st.selectbox(
    "이름 또는 교번을 검색하세요:",
    options=["선택 안 함"] + user_options,
    index=0
)

if selected_label != "선택 안 함":
    target_pid = user_id_map[selected_label]
    target_u = get_user(target_pid)
    target_songs = df_songs[df_songs['proposer'] == target_pid].copy()
    user_row = df_base_stat[df_base_stat['student_id'] == target_pid].iloc[0]
    
    p_total_songs = len(target_songs)
    p_approved = int((target_songs['approved'] == True).sum())
    p_rate = round((p_approved / p_total_songs) * 100, 1)
    p_net = int(target_songs['net_votes'].sum())
    p_agree = int(target_songs['agree'].sum())
    p_disagree = int(target_songs['disagree'].sum())
    p_avg_net = round(float(target_songs['net_votes'].mean()), 2)
    p_avg_agree = round(float(target_songs['agree'].mean()), 2)
    p_avg_disagree = round(float(target_songs['disagree'].mean()), 2)
    p_score = user_row['score']
    
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
            <span>🏆 <b>시즌 랭킹</b></span>
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

    target_songs['주차'] = target_songs['year'].astype(str) + "년 " + target_songs['week'].astype(str) + "주"
    chart_data = target_songs[['주차', 'net_votes', 'agree', 'disagree']].rename(columns={
        'net_votes': '순합산(Net)',
        'agree': '좋아요',
        'disagree': '싫어요'
    }).set_index('주차')
    
    st.caption("📈 주차별 신청곡 득표 추이")
    st.line_chart(chart_data)

# -------------------------------------------------------------
# 11. 📊 전교생 종합 기록실 (클릭 시 정렬 테이블)
# -------------------------------------------------------------
st.markdown("<div class='section-header'>📋 전교생 종합 통계 기록실 <span style='font-size: 13px; font-weight: normal; color: #64748b;'>(※ 규정: 신청 곡 수 4개 이상만 상단 순위 진입, 미달 시 하단 '-')</span></div>", unsafe_allow_html=True)

table_data_json = json.dumps(df_base_stat.to_dict(orient='records'))

html_table_component = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {{
        box-sizing: border-box;
        font-family: 'Pretendard', sans-serif;
    }}
    body {{
        margin: 0;
        padding: 0;
        background-color: transparent;
    }}
    .table-card {{
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        overflow-x: auto;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        text-align: right;
        font-size: 13.5px;
        white-space: nowrap;
    }}
    th {{
        background: #f8fafc;
        color: #64748b;
        font-weight: 700;
        padding: 12px 10px;
        border-bottom: 2px solid #e2e8f0;
        cursor: pointer;
        user-select: none;
        transition: background 0.2s;
    }}
    th:hover {{
        background: #eef2f6;
        color: #1e293b;
    }}
    th.active {{
        color: #2563eb;
    }}
    th.active .sort-arrow {{
        opacity: 1;
        color: #2563eb;
    }}
    .sort-arrow {{
        display: inline-block;
        font-size: 10px;
        margin-left: 4px;
        opacity: 0.3;
        transition: transform 0.2s ease;
    }}
    .sort-arrow.desc {{
        transform: rotate(180deg);
    }}
    td {{
        padding: 10px;
        border-bottom: 1px solid #f1f5f9;
        color: #1e293b;
    }}
    tr:hover td {{
        background-color: #f8fafc;
    }}
    .col-rank {{
        text-align: center;
        font-weight: 700;
        color: #94a3b8;
        width: 45px;
    }}
    .col-rank.unqualified {{
        color: #cbd5e1;
        font-size: 15px;
    }}
    .col-user {{
        text-align: left;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .avatar {{
        width: 28px;
        height: 28px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid #e2e8f0;
    }}
    .user-name {{
        font-weight: 600;
        color: #0f172a;
    }}
    .highlight-cell {{
        font-weight: 700;
        color: #2563eb;
    }}
</style>
</head>
<body>

<div class="table-card">
    <table id="statsTable">
        <thead>
            <tr>
                <th style="cursor: default; text-align: center;">순위</th>
                <th onclick="sortTable('name')" style="text-align: left;">선수/이름 <span class="sort-arrow" id="arrow-name">▲</span></th>
                <th onclick="sortTable('student_id')">교번 <span class="sort-arrow" id="arrow-student_id">▲</span></th>
                <th onclick="sortTable('score')" class="active">종합 점수 <span class="sort-arrow desc" id="arrow-score">▲</span></th>
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

<script>
    let rawData = {table_data_json};
    let currentKey = 'score';
    let isAsc = false;

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
                    <div class="col-user">
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

    // 초기 정렬: 종합 점수 내림차순
    const initialData = doSort('score', false);
    renderTable(initialData);
</script>
</body>
</html>
"""

st.components.v1.html(html_table_component, height=750, scrolling=True)
