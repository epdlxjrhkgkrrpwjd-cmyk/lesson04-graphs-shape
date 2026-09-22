import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 장르: 세로막대(|)로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre_main"] = df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())

    # 개봉일(여덟 자리 숫자) -> datetime 변환
    df["openDt_str"] = df["openDt"].astype(str).str.zfill(8)
    df["openDt_date"] = pd.to_datetime(df["openDt_str"], format="%Y%m%d", errors="coerce")
    df["openYear"] = df["openDt_date"].dt.year

    return df


df = load_data()

# ----------------------------------------------------------------------------
# 헤더
# ----------------------------------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    """
1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한 **216편**의 데이터를 살펴봅니다.
각 그래프는 영화 데이터가 어떻게 **분포**하고, 서로 어떤 **관계**를 맺는지 보여줍니다.
"""
)

with st.expander("📄 원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ----------------------------------------------------------------------------
st.header("1️⃣ 장르별 영화 편수")

genre_counts = df["genre_main"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig1 = go.Figure(
    data=[
        go.Pie(
            labels=genre_counts["genre"],
            values=genre_counts["count"],
            hole=0.5,
            hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
        )
    ]
)
fig1.update_layout(
    title="장르별 영화 편수 (도넛 그래프)",
    legend_title="장르",
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 장르별 편수 그래프를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 2. 장르 안 영화 트리맵 - 크기는 total_audi
# ----------------------------------------------------------------------------
st.header("2️⃣ 장르별 영화 트리맵 (크기 = 총 관객수)")

fig_tree = px.treemap(
    df,
    path=[px.Constant("전체"), "genre_main", "movieNm"],
    values="total_audi",
    color="genre_main",
    custom_data=["movieNm", "total_audi"],
)
fig_tree.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>총 관객수: %{customdata[1]:,}명<extra></extra>"
)
fig_tree.update_layout(title="장르 안 영화 트리맵 (칸 크기 = 총 관객수)")
st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 장르별 영화 트리맵을 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 3. 총 관객수 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("3️⃣ 총 관객수 분포")

fig2 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    labels={"total_audi": "총 관객수"},
    title="영화별 총 관객수 분포",
)
fig2.update_traces(hovertemplate="총 관객수 구간: %{x}<br>영화 편수: %{y}<extra></extra>")
fig2.update_layout(yaxis_title="영화 편수")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 총 관객수 분포 그래프를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 4. 개봉일 스크린수 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("4️⃣ 개봉일 스크린수 분포")

fig3 = px.histogram(
    df,
    x="first_scrn",
    nbins=30,
    labels={"first_scrn": "개봉일 스크린수"},
    title="영화별 개봉일 스크린수 분포",
    color_discrete_sequence=["#EF553B"],
)
fig3.update_traces(hovertemplate="스크린수 구간: %{x}<br>영화 편수: %{y}<extra></extra>")
fig3.update_layout(yaxis_title="영화 편수")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 개봉일 스크린수 분포 그래프를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 5. 개봉일 스크린수 vs 총 관객수 - 산점도
# ----------------------------------------------------------------------------
st.header("5️⃣ 개봉일 스크린수와 총 관객수의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수", "genre_main": "장르"},
    title="개봉일 스크린수 vs 총 관객수",
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 스크린수와 총 관객수의 관계를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 6. 개봉 첫 주 관객수 vs 총 관객수 - 산점도
# ----------------------------------------------------------------------------
st.header("6️⃣ 개봉 첫 주 관객수와 총 관객수의 관계")

fig5 = px.scatter(
    df,
    x="first_week_audi",
    y="total_audi",
    color="genre_main",
    size="days_in_top10",
    hover_name="movieNm",
    labels={
        "first_week_audi": "개봉 첫 주 관객수",
        "total_audi": "총 관객수",
        "genre_main": "장르",
        "days_in_top10": "10위권 유지일수",
    },
    title="개봉 첫 주 관객수 vs 총 관객수 (원 크기 = 10위권 유지일수)",
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 첫 주 관객수와 총 관객수의 관계를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 7. 10위권 유지일수 분포 - 박스플롯 (장르별)
# ----------------------------------------------------------------------------
st.header("7️⃣ 장르별 10위권 유지일수 분포")

fig6 = px.box(
    df,
    x="genre_main",
    y="days_in_top10",
    color="genre_main",
    labels={"genre_main": "장르", "days_in_top10": "10위권 유지일수"},
    title="장르별 10위권 유지일수 분포",
)
fig6.update_layout(showlegend=False)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 장르별 10위권 유지일수 분포를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

st.caption("데이터 출처: KOBIS (영화진흥위원회) · greatsong/modudata")
