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

    # 제작 국가: 한국 영화 vs 외국 영화 구분
    df["nation_group"] = df["nation"].astype(str).apply(lambda x: "한국 영화" if "한국" in x else "외국 영화")

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
# 그래프 3. 총 관객수 히스토그램 - 집중 구간 및 최고 흥행작
# ----------------------------------------------------------------------------
st.header("3️⃣ 총 관객수 히스토그램")

N_BINS = 30
fig_audi_hist = px.histogram(
    df,
    x="total_audi",
    nbins=N_BINS,
    labels={"total_audi": "총 관객수"},
    title="영화별 총 관객수 히스토그램",
    color_discrete_sequence=["#636EFA"],
)
fig_audi_hist.update_traces(hovertemplate="총 관객수 구간: %{x}<br>영화 편수: %{y}편<extra></extra>")
fig_audi_hist.update_layout(yaxis_title="영화 편수")
st.plotly_chart(fig_audi_hist, use_container_width=True)

# 가장 영화가 많이 몰린 구간 계산
audi_bins, bin_edges = pd.cut(df["total_audi"], bins=N_BINS, retbins=True)
bin_counts = audi_bins.value_counts()
top_bin = bin_counts.idxmax()
top_bin_count = bin_counts.max()

# 총 관객수 1위 영화 계산
top_movie_row = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = top_movie_row["total_audi"]

st.markdown(
    f"- 영화가 가장 많이 몰려 있는 총 관객수 구간은 **약 {top_bin.left:,.0f}명 ~ {top_bin.right:,.0f}명**이며, "
    f"이 구간에 **{top_bin_count}편**의 영화가 속해 있습니다."
)
st.markdown(
    f"- 총 관객수가 가장 많은 영화는 **'{top_movie_name}'**이며, 총 **{top_movie_audi:,.0f}명**의 관객을 동원했습니다."
)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 총 관객수 히스토그램을 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 4. 개봉일 스크린수 vs 총 관객수 - 산점도
# ----------------------------------------------------------------------------
st.header("4️⃣ 개봉일 스크린수와 총 관객수의 관계")

fig_scrn_audi = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수", "genre_main": "장르"},
    title="개봉일 스크린수 vs 총 관객수 (장르별 색상)",
)
st.plotly_chart(fig_scrn_audi, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 개봉일 스크린수와 총 관객수의 관계를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 5. 영화 10편 이상 장르의 총 관객수 박스플롯
# ----------------------------------------------------------------------------
st.header("5️⃣ 영화 10편 이상 장르의 총 관객수 박스플롯")

genre_movie_counts = df["genre_main"].value_counts()
eligible_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_eligible = df[df["genre_main"].isin(eligible_genres)]

fig_box5 = px.box(
    df_eligible,
    x="genre_main",
    y="total_audi",
    color="genre_main",
    points="outliers",
    hover_name="movieNm",
    labels={"genre_main": "장르", "total_audi": "총 관객수"},
    title="영화 10편 이상인 장르별 총 관객수 박스플롯",
)
fig_box5.update_layout(showlegend=False, yaxis_title="총 관객수", xaxis_title="장르")
st.plotly_chart(fig_box5, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 장르별 총 관객수 박스플롯을 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 6. 개봉일 스크린수 vs 총 관객수 - 버블 그래프 (크기 = 첫 주 관객수)
# ----------------------------------------------------------------------------
st.header("6️⃣ 개봉일 스크린수와 총 관객수의 관계 (버블 그래프)")

fig_bubble6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    size="first_week_audi",
    hover_name="movieNm",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre_main": "장르",
        "first_week_audi": "개봉 첫 주 관객수",
    },
    title="개봉일 스크린수 vs 총 관객수 (원 크기 = 개봉 첫 주 관객수)",
)
st.plotly_chart(fig_bubble6, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 스크린수·총 관객수·첫 주 관객수 세 가지의 관계를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 7. 제작 국가 -> 장르 선버스트 (크기 = 영화 편수)
# ----------------------------------------------------------------------------
st.header("7️⃣ 제작 국가별 장르 선버스트")

fig_sun7 = px.sunburst(
    df,
    path=["nation", "genre_main"],
    labels={"nation": "제작 국가", "genre_main": "장르"},
    title="제작 국가 → 장르 선버스트 (칸 크기 = 영화 편수)",
)
fig_sun7.update_traces(hovertemplate="%{label}<br>영화 편수: %{value}편<extra></extra>")
st.plotly_chart(fig_sun7, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 제작 국가별 장르 선버스트 그래프를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 8. 내 질문 - 국가별 총 관객수 비교 [한국 영화 vs 외국 영화]
# ----------------------------------------------------------------------------
st.header("8️⃣ 국가별 총 관객수 비교 [한국 영화 vs 외국 영화]")

fig_nation8 = px.bar(
    df,
    x="nation_group",
    y="total_audi",
    color="nation_group",
    hover_name="movieNm",
    color_discrete_map={"한국 영화": "#EF553B", "외국 영화": "#636EFA"},
    labels={"nation_group": "", "total_audi": "총 관객수"},
    title="한국 영화와 외국 영화의 총 관객수 비교",
)
fig_nation8.update_traces(
    hovertemplate="영화명: %{hovertext}<br>총 관객수: %{y:,.0f}명<extra></extra>",
    marker_line_color="white",
    marker_line_width=0.5,
)
fig_nation8.update_layout(showlegend=False, yaxis_title="총 관객수", xaxis_title="")
st.plotly_chart(fig_nation8, use_container_width=True)

st.markdown("**💡 이 그래프로 알 수 있는 것:** ")
st.info("여기에 한국 영화와 외국 영화의 총 관객수 비교 결과를 보고 알게 된 점을 한 문장으로 적어 보세요.")

st.divider()

# ----------------------------------------------------------------------------
# 그래프 9. 총 관객수 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("9️⃣ 총 관객수 분포")

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
# 그래프 10. 개봉일 스크린수 분포 - 히스토그램
# ----------------------------------------------------------------------------
st.header("🔟 개봉일 스크린수 분포")

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
# 그래프 11. 개봉일 스크린수 vs 총 관객수 - 산점도
# ----------------------------------------------------------------------------
st.header("1️⃣1️⃣ 개봉일 스크린수와 총 관객수의 관계")

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
# 그래프 12. 개봉 첫 주 관객수 vs 총 관객수 - 산점도
# ----------------------------------------------------------------------------
st.header("1️⃣2️⃣ 개봉 첫 주 관객수와 총 관객수의 관계")

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
# 그래프 13. 10위권 유지일수 분포 - 박스플롯 (장르별)
# ----------------------------------------------------------------------------
st.header("1️⃣3️⃣ 장르별 10위권 유지일수 분포")

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

st.divider()

st.caption("데이터 출처: KOBIS (영화진흥위원회) · greatsong/modudata")
