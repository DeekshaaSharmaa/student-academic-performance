
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Student Performance | DA-003",
    page_icon="🎓",
    layout="wide"
)

PASS_MARK = 40

SUBJECTS = [
    "Mathematics",
    "Python_Programming",
    "Computer_Fundamentals",
    "English",
    "Statistics"
]

# Theme colours
TEAL = "#1F5F5B"
CLAY = "#D9663B"
CREAM = "#FAF7F2"
PALE = "#F0EBE1"
DARK = "#263B36"

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #FAF7F2;
    color: #263B36;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #1F5F5B !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stMetric"] {
    background: #F0EBE1;
    padding: 20px 18px;
    border-radius: 14px;
    border: 1px solid #E4DCCE;
    transition: 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #1F5F5B;
    transform: translateY(-3px);
}

[data-testid="stMetricLabel"] {
    color: #52645D !important;
    font-size: 14px;
}

[data-testid="stMetricValue"] {
    color: #1F5F5B !important;
    font-weight: 700;
}

[data-testid="stSidebar"] {
    background-color: #F0EBE1;
}

[data-testid="stSidebar"] h2 {
    color: #1F5F5B;
}

hr {
    border-color: #E4DCCE;
}

div[data-testid="stVerticalBlock"] > div:has(> div.stButton) {
    transition: 0.2s ease;
}

.stCaption {
    color: #687B72;
}
</style>
""", unsafe_allow_html=True)
# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv(
        "data/processed/student_performance_clean.csv"
    )

    data["Average_Marks"] = data[SUBJECTS].mean(axis=1).round(2)

    return data


df = load_data()




# ---------------- HERO SECTION ----------------
# HERO SECTION

st.markdown("# Student Academic Performance")
st.markdown(
    "### Understanding student results through data"
)

st.write(
    "An education analytics dashboard exploring "
    "marks, attendance and study habits."
)

st.divider()
# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.markdown("## Dashboard Controls")
st.sidebar.caption("Customize the student data you want to explore.")

sections = st.sidebar.multiselect(
    "Select Section",
    sorted(df["Section"].dropna().unique()),
    default=sorted(df["Section"].dropna().unique())
)

genders = st.sidebar.multiselect(
    "Select Gender",
    sorted(df["Gender"].dropna().unique()),
    default=sorted(df["Gender"].dropna().unique())
)

att_min, att_max = st.sidebar.slider(
    "Attendance Range (%)",
    0, 100, (0, 100)
)

f = df[
    df["Section"].isin(sections)
    & df["Gender"].isin(genders)
    & df["Attendance_Percent"].between(att_min, att_max)
]

if len(f) < 5:
    st.warning("Too few students for these filters. Please widen your selection.")
    st.stop()


# ---------------- KPI SECTION ----------------
st.markdown("## Performance Overview")
st.caption("A quick summary of the currently selected students.")

passed_all = (
    (f[SUBJECTS] >= PASS_MARK).all(axis=1).mean() * 100
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Students", f"{len(f):,}")
c2.metric("Average Marks", f"{f['Average_Marks'].mean():.1f}/100")
c3.metric("Passed All Subjects", f"{passed_all:.1f}%")
c4.metric("Average Attendance", f"{f['Attendance_Percent'].mean():.1f}%")


st.divider()


# ---------------- CHART STYLE HELPER ----------------
def new_chart():
    fig, ax = plt.subplots(figsize=(7, 4))

    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_color("#D8D2C7")
    ax.spines["bottom"].set_color("#D8D2C7")

    ax.tick_params(colors=DARK)

    return fig, ax


# ---------------- SUBJECT PERFORMANCE ----------------
st.markdown("## 01 · Subject-wise Performance")
st.caption("Compare average marks and pass percentages across subjects.")

means = f[SUBJECTS].mean().round(2)

pass_pct = (
    (f[SUBJECTS] >= PASS_MARK).mean() * 100
).round(1)

left, right = st.columns([1.5, 1])

with left:
    fig, ax = new_chart()

    sns.barplot(
        x=means.index,
        y=means.values,
        color=TEAL,
        ax=ax
    )

    ax.set_title("Average Marks by Subject", pad=15, fontsize=14)
    ax.set_xlabel("")
    ax.set_ylabel("Average Marks")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=20)

    st.pyplot(fig)
    plt.close(fig)

with right:
    st.markdown("#### Subject Pass Percentage")

    pass_table = pd.DataFrame({
        "Subject": pass_pct.index,
        "Pass Percentage": pass_pct.values
    })

    st.dataframe(
        pass_table,
        hide_index=True,
        use_container_width=True
    )


st.divider()


# ---------------- PERFORMANCE CATEGORIES ----------------
st.markdown("## 02 · Student Performance Categories")
st.caption("Understand how students are distributed across performance levels.")

def performance_category(mark):
    if mark >= 80:
        return "Excellent"
    elif mark >= 60:
        return "Good"
    elif mark >= 40:
        return "Average"
    else:
        return "Needs Support"


f = f.copy()

f["Performance_Category"] = f["Average_Marks"].apply(
    performance_category
)

category_order = [
    "Excellent",
    "Good",
    "Average",
    "Needs Support"
]

category_counts = (
    f["Performance_Category"]
    .value_counts()
    .reindex(category_order, fill_value=0)
)

category_colours = [
    "#1F5F5B",
    "#6E9D91",
    "#E5B85C",
    "#D9663B"
]

left, right = st.columns([1, 1])

with left:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.pie(
        category_counts,
        labels=None,
        startangle=90,
        colors=category_colours,
        wedgeprops={
            "width": 0.38,
            "edgecolor": CREAM,
            "linewidth": 3
        }
    )

    # Display the total number of selected students in the centre.
    ax.text(
        0, 0.08,
        f"{len(f)}",
        ha="center",
        va="center",
        fontsize=25,
        fontweight="bold",
        color=TEAL
    )

    ax.text(
        0, -0.15,
        "Students",
        ha="center",
        va="center",
        fontsize=11,
        color=DARK
    )

    ax.set_title(
        "Performance Distribution",
        fontsize=15,
        color=TEAL,
        pad=18
    )

    st.pyplot(fig)
    plt.close(fig)

with right:
    st.markdown("#### Category Summary")

    for category, count in category_counts.items():
        percentage = count / len(f) * 100
        st.write(f"**{category}** — {count} students ({percentage:.1f}%)")

    st.caption(
        "Categories are based on average marks: "
        "Excellent 80+, Good 60–79, Average 40–59, Needs Support below 40."
    )

st.divider()


# ---------------- ATTENDANCE AND STUDY TIME ----------------
st.markdown("## 03 · Attendance & Study Habits")
st.caption("Explore how attendance and weekly study hours are associated with marks.")

a, b = st.columns(2)

with a:
    fig, ax = new_chart()

    sns.regplot(
        data=f,
        x="Attendance_Percent",
        y="Average_Marks",
        scatter_kws={"alpha": 0.6, "color": TEAL},
        line_kws={"color": CLAY},
        ax=ax
    )

    ax.set_title("Attendance vs Average Marks")
    ax.set_xlabel("Attendance (%)")
    ax.set_ylabel("Average Marks")

    st.pyplot(fig)
    plt.close(fig)

with b:
    fig, ax = new_chart()

    sns.regplot(
        data=f,
        x="Study_Hours_Per_Week",
        y="Average_Marks",
        scatter_kws={"alpha": 0.6, "color": TEAL},
        line_kws={"color": CLAY},
        ax=ax
    )

    ax.set_title("Study Hours vs Average Marks")
    ax.set_xlabel("Study Hours per Week")
    ax.set_ylabel("Average Marks")

    st.pyplot(fig)
    plt.close(fig)


st.divider()


# ---------------- CORRELATION ----------------
st.markdown("## 04 · Correlation Analysis")
st.caption("Examine the strength and direction of relationships between numerical variables.")

cols = [
    "Attendance_Percent",
    "Study_Hours_Per_Week"
] + SUBJECTS + ["Average_Marks"]

corr = f[cols].corr().round(2)

fig, ax = plt.subplots(figsize=(10, 6))

fig.patch.set_facecolor(CREAM)

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    center=0,
    cmap=sns.diverging_palette(20, 180, as_cmap=True),
    ax=ax,
    linewidths=0.5
)

ax.set_title("Correlation Heatmap", pad=15)

st.pyplot(fig)
plt.close(fig)


st.divider()


# ---------------- KEY FINDINGS ----------------
st.markdown("## 05 · Key Findings")
st.caption("Important observations from the selected dataset.")

def describe_r(r):
    if pd.isna(r):
        return "not available"

    size = abs(r)

    if size >= 0.6:
        strength = "strong"
    elif size >= 0.3:
        strength = "moderate"
    else:
        strength = "weak"

    direction = "positive" if r > 0 else "negative"

    return f"{strength} {direction}"


r_att = f["Attendance_Percent"].corr(f["Average_Marks"])
r_study = f["Study_Hours_Per_Week"].corr(f["Average_Marks"])

find1, find2 = st.columns(2)

with find1:
    st.info(
        f"**Highest average subject:** {means.idxmax()} "
        f"({means.max():.1f} marks)"
    )

    st.info(
        f"**Lowest average subject:** {means.idxmin()} "
        f"({means.min():.1f} marks)"
    )

with find2:
    st.info(
        f"**Attendance association:** {describe_r(r_att)} "
        f"(r = {r_att:.2f})"
    )

    st.info(
        f"**Study-time association:** {describe_r(r_study)} "
        f"(r = {r_study:.2f})"
    )

st.success(
    f"{passed_all:.1f}% of selected students passed all subjects "
    f"using a pass mark of {PASS_MARK}."
)


# ---------------- FOOTER ----------------
st.markdown("""
<br>
<div style="
    background: #F0EBE1;
    padding: 22px;
    border-radius: 14px;
    text-align: center;
    border-top: 3px solid #1F5F5B;
">
    <p style="color: #1F5F5B; font-weight: 700; margin-bottom: 5px;">
        STUDENT ACADEMIC PERFORMANCE ANALYSIS
    </p>
    <p style="color: #687B72; font-size: 13px; margin: 0;">
        DA-003 · Education Analytics · Python & Streamlit
    </p>
    <p style="color: #687B72; font-size: 12px; margin-top: 10px;">
        Correlation indicates association, not causation.
        This dashboard uses synthetic student data.
    </p>
</div>
""", unsafe_allow_html=True)
