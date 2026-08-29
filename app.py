import streamlit as st
import requests
import pandas as pd
import json

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="SSHS 기상곡 리더보드 & 전교생 통계",
    page_icon="🎵",
    layout="wide"
)

# 2. 커스텀 CSS
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
        margin: 30px 0 16px 0;
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

# 4. 상단 카드 렌더링 함수
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

# 5. 상단 랭킹 데이터 집계
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

# 6. 상단 카드 UI 렌더링
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
# 7. 📊 전교생 종합 기록실 (클릭 시 세모 회전 인터랙티브 테이블)
# -------------------------------------------------------------
st.markdown("<div class='section-header'>📋 전교생 종합 통계 기록실</div>", unsafe_allow_html=True)

first_map = first_cnt_df.set_index('proposer')['first_cnt'].to_dict()
last_map = last_cnt_df.set_index('proposer')['last_cnt'].to_dict()

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
        "last_cnt": last_cnt
    })

# JSON으로 전달하여 프론트엔드에서 원클릭 삼각형 정렬 구현
table_data_json = json.dumps(stat_records)

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
                <th onclick="sortTable('total_net')" class="active">순합산(Net) <span class="sort-arrow desc" id="arrow-total_net">▲</span></th>
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
    let data = {table_data_json};
    let currentKey = 'total_net';
    let isAsc = false;

    function renderTable() {{
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        
        data.forEach((row, idx) => {{
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="col-rank">${{idx + 1}}</td>
                <td>
                    <div class="col-user">
                        <img class="avatar" src="${{row.pfp}}" onerror="this.src='{default_pfp}'"/>
                        <span class="user-name">${{row.name}}</span>
                    </div>
                </td>
                <td>${{row.student_id}}</td>
                <td class="highlight-cell">${{row.total_net > 0 ? '+' + row.total_net : row.total_net}}</td>
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

    function sortTable(key) {{
        if (currentKey === key) {{
            isAsc = !isAsc;
        }} else {{
            currentKey = key;
            isAsc = (key === 'name' || key === 'student_id') ? true : false;
        }}

        // 정렬 수행
        data.sort((a, b) => {{
            let valA = a[key];
            let valB = b[key];
            if (typeof valA === 'string') {{
                return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }}
            return isAsc ? valA - valB : valB - valA;
        }});

        // 세모 화살표 스타일 업데이트 (180도 회전 애니메이션)
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

        renderTable();
    }}

    // 초기 렌더링
    data.sort((a, b) => b.total_net - a.total_net);
    renderTable();
</script>
</body>
</html>
"""

# HTML 컴포넌트로 테이블 삽입 (높이 750px 스크롤)
st.components.v1.html(html_table_component, height=750, scrolling=True)
