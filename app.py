"""
Customer Shopping Behavior — Analytics Dashboard
--------------------------------------------------
An interactive Streamlit app exploring a retail customer transactions
dataset (3,900 records / 18 attributes). Built around a set of concrete
analytical questions, each answered with an interactive visualization
and a written finding.

Run with:
    streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Shopping Behavior Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILENAME = "customer_shopping_behavior (1).csv"

# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_FILENAME = "customer_shopping_behavior (1).csv"
DATA_PATH = BASE_DIR / DATA_FILENAME




from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_FILENAME = "customer_shopping_behavior (1).csv"
DATA_PATH = BASE_DIR / DATA_FILENAME




from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA = BASE_DIR / "customer_shopping_behavior (1).csv"


@st.cache_data
def load_data(data_source):
    if data_source is not None:
        return pd.read_csv(data_source)

    if DEFAULT_DATA.exists():
        return pd.read_csv(DEFAULT_DATA)

    st.error(
        f"Dataset not found. Please upload a CSV file or place "
        f"'{DEFAULT_DATA.name}' in the project folder."
    )
    st.stop()


data_source = st.file_uploader(
    "Upload a CSV dataset (optional)",
    type=["csv"]
)


df_raw = load_data(data_source)


df = load_data(data_source)

def get_data_source():
    """Prefer a bundled CSV sitting next to app.py; otherwise ask for upload."""
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILENAME)
    if os.path.exists(local_path):
        return local_path
    uploaded = st.sidebar.file_uploader("Upload customer_shopping_behavior.csv", type="csv")
    return uploaded


data_source = get_data_source()
if data_source is None:
    st.title("🛍️ Customer Shopping Behavior Analytics")
    st.info("Upload the dataset (CSV) in the sidebar to get started.")
    st.stop()

df_raw = load_data(data_source)

# ----------------------------------------------------------------------
# Sidebar — global filters
# ----------------------------------------------------------------------
st.sidebar.header("Filters")

genders = st.sidebar.multiselect(
    "Gender", options=sorted(df_raw["Gender"].unique()), default=list(sorted(df_raw["Gender"].unique()))
)
categories = st.sidebar.multiselect(
    "Category", options=sorted(df_raw["Category"].unique()), default=list(sorted(df_raw["Category"].unique()))
)
seasons = st.sidebar.multiselect(
    "Season", options=sorted(df_raw["Season"].unique()), default=list(sorted(df_raw["Season"].unique()))
)
age_range = st.sidebar.slider(
    "Age range", int(df_raw["Age"].min()), int(df_raw["Age"].max()),
    (int(df_raw["Age"].min()), int(df_raw["Age"].max()))
)

df = df_raw[
    df_raw["Gender"].isin(genders)
    & df_raw["Category"].isin(categories)
    & df_raw["Season"].isin(seasons)
    & df_raw["Age"].between(age_range[0], age_range[1])
].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(df):,}** of {len(df_raw):,} records after filters.")

# ----------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------
st.title("🛍️ Customer Shopping Behavior Analytics")
st.caption(
    "Exploratory & analytical deep-dive into retail transaction data — revenue drivers, "
    "discount effects, loyalty patterns, and demographic behavior."
)

if df.empty:
    st.warning("No records match the current filters. Adjust the sidebar selections.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers", f"{df['Customer ID'].nunique():,}")
k2.metric("Total Revenue", f"${df['Purchase Amount (USD)'].sum():,.0f}")
k3.metric("Avg Order Value", f"${df['Purchase Amount (USD)'].mean():.2f}")
k4.metric("Avg Review Rating", f"{df['Review Rating'].mean():.2f} / 5")
k5.metric("Subscribers", f"{(df['Subscription Status'] == 'Yes').mean()*100:.1f}%")

st.markdown("---")

# ----------------------------------------------------------------------
# Tabs = analytical questions
# ----------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📦 Category & Revenue",
    "🏷️ Discounts & Promotions",
    "👥 Demographics",
    "🔁 Loyalty & Frequency",
    "🍂 Seasonality",
    "🔗 Correlations",
    "⚠️ Data Quality Notes",
])

# ========================================================================
# TAB 1 — Category & Revenue
# ========================================================================
with tab1:
    st.subheader("Which categories and items drive revenue?")

    col1, col2 = st.columns([1.2, 1])
    with col1:
        cat_rev = (
            df.groupby("Category")["Purchase Amount (USD)"]
            .agg(Total="sum", Average="mean", Orders="count")
            .sort_values("Total", ascending=False)
            .reset_index()
        )
        fig = px.bar(
            cat_rev, x="Category", y="Total", text_auto=".2s",
            title="Total Revenue by Category", color="Category",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            cat_rev, names="Category", values="Orders",
            title="Share of Orders by Category", hole=0.45,
        )
        st.plotly_chart(fig2, use_container_width=True)

    top_items = df["Item Purchased"].value_counts().head(10).reset_index()
    top_items.columns = ["Item", "Count"]
    fig3 = px.bar(top_items.sort_values("Count"), x="Count", y="Item", orientation="h",
                   title="Top 10 Best-Selling Items")
    st.plotly_chart(fig3, use_container_width=True)

    top_cat = cat_rev.iloc[0]
    st.markdown(
        f"""
**Finding:** *{top_cat['Category']}* generates the highest total revenue
(**${top_cat['Total']:,.0f}**, {cat_rev['Orders'][0]} orders), but average order value is
remarkably flat across categories (**${cat_rev['Average'].min():.2f}–${cat_rev['Average'].max():.2f}**).
This means the revenue gap between categories is driven almost entirely by **purchase volume /
catalog breadth**, not by higher basket sizes — a signal that cross-sell and catalog-expansion
strategies in lower-volume categories (e.g. Outerwear) may be more effective than trying to
upsell within already-strong categories.
"""
    )

# ========================================================================
# TAB 2 — Discounts & Promotions
# ========================================================================
with tab2:
    st.subheader("Do discounts and promo codes actually change buying behavior?")

    col1, col2 = st.columns(2)
    with col1:
        disc = df.groupby("Discount Applied")["Purchase Amount (USD)"].mean().reset_index()
        fig = px.bar(disc, x="Discount Applied", y="Purchase Amount (USD)",
                     title="Avg Purchase Amount: Discount vs No Discount",
                     color="Discount Applied", text_auto=".2f")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ship_disc = pd.crosstab(df["Shipping Type"], df["Discount Applied"], normalize="index") * 100
        ship_disc = ship_disc.reset_index().melt(id_vars="Shipping Type", var_name="Discount Applied", value_name="Pct")
        fig2 = px.bar(ship_disc, x="Shipping Type", y="Pct", color="Discount Applied", barmode="group",
                      title="Discount Usage Rate by Shipping Type (%)")
        st.plotly_chart(fig2, use_container_width=True)

    promo_align = pd.crosstab(df["Promo Code Used"], df["Discount Applied"])
    st.markdown("**Promo Code Used vs Discount Applied (cross-tab):**")
    st.dataframe(promo_align, use_container_width=True)

    avg_no = df.loc[df["Discount Applied"] == "No", "Purchase Amount (USD)"].mean()
    avg_yes = df.loc[df["Discount Applied"] == "Yes", "Purchase Amount (USD)"].mean()
    diff_pct = (avg_yes - avg_no) / avg_no * 100 if avg_no else 0
    st.markdown(
        f"""
**Finding:** Average spend with a discount (**${avg_yes:.2f}**) is essentially identical to
spend without one (**${avg_no:.2f}**, a **{diff_pct:+.1f}%** difference) — discounts are not
associated with larger basket sizes in this dataset. The cross-tab also shows **Promo Code Used**
and **Discount Applied** are perfectly redundant (identical values row-for-row), meaning in this
dataset the two columns encode the same underlying event rather than two independent behaviors —
worth flagging for feature de-duplication before any modeling.
"""
    )
    
# ---------------------------------------------------------
# Feature Engineering: Age Groups
# ---------------------------------------------------------

df["Age Group"] = pd.cut(
    df["Age"],
    bins=[0, 24, 34, 44, 54, 64, 100],
    labels=[
        "18-24",
        "25-34",
        "35-44",
        "45-54",
        "55-64",
        "65+"
    ],
    include_lowest=True
)

# ========================================================================
# TAB 3 — Demographics
# ========================================================================
with tab3:
    st.subheader("How do age and gender relate to spending and category preference?")

    col1, col2 = st.columns(2)
    with col1:
        age_spend = df.groupby("Age Group", observed=True)["Purchase Amount (USD)"].mean().reset_index()
        fig = px.line(age_spend, x="Age Group", y="Purchase Amount (USD)", markers=True,
                      title="Average Spend by Age Group")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        gender_cat = pd.crosstab(df["Gender"], df["Category"], normalize="index") * 100
        gender_cat = gender_cat.reset_index().melt(id_vars="Gender", var_name="Category", value_name="Pct")
        fig2 = px.bar(gender_cat, x="Category", y="Pct", color="Gender", barmode="group",
                      title="Category Mix by Gender (% within gender)")
        st.plotly_chart(fig2, use_container_width=True)

    gender_sub = pd.crosstab(df["Gender"], df["Subscription Status"], normalize="index") * 100
    fig3 = px.bar(gender_sub.reset_index().melt(id_vars="Gender", var_name="Subscription Status", value_name="Pct"),
                  x="Gender", y="Pct", color="Subscription Status", barmode="stack",
                  title="Subscription Rate by Gender (%)")
    st.plotly_chart(fig3, use_container_width=True)

    spend_range = age_spend["Purchase Amount (USD)"].max() - age_spend["Purchase Amount (USD)"].min()
    female_sub_rate = gender_sub.loc["Female", "Yes"] if "Female" in gender_sub.index and "Yes" in gender_sub.columns else 0
    st.markdown(
        f"""
**Finding:** Average spend barely moves across age groups (range of only
**${spend_range:.2f}**), so age is not a meaningful spend predictor here. The subscription
chart is the standout: **{female_sub_rate:.0f}% of female customers hold a subscription**, versus
a substantial share of male customers — i.e. in this dataset subscription status is almost
entirely concentrated in one gender, which is unusual for a real retail population and should be
treated as a data-generation artifact rather than a genuine market insight (see *Data Quality*
tab).
"""
    )

# ========================================================================
# TAB 4 — Loyalty & Frequency
# ========================================================================
with tab4:
    st.subheader("Does purchase frequency or subscription status predict loyalty?")

    col1, col2 = st.columns(2)
    with col1:
        freq_loyal = df.groupby("Frequency of Purchases", observed=True)["Previous Purchases"].mean().reset_index()
        fig = px.bar(freq_loyal, x="Frequency of Purchases", y="Previous Purchases",
                     title="Avg Previous Purchases by Stated Frequency")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sub_compare = df.groupby("Subscription Status")[["Purchase Amount (USD)", "Previous Purchases", "Review Rating"]].mean().reset_index()
        sub_melt = sub_compare.melt(id_vars="Subscription Status", var_name="Metric", value_name="Value")
        fig2 = px.bar(sub_melt, x="Metric", y="Value", color="Subscription Status", barmode="group",
                      title="Subscribers vs Non-Subscribers")
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(df, x="Previous Purchases", nbins=25, title="Distribution of Previous Purchases")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
        """
**Finding:** Customers who *say* they buy weekly or quarterly show almost the same historical
purchase counts as those who say they buy annually — self-reported frequency does not track
observed loyalty (previous purchases). Likewise, subscribers and non-subscribers look nearly
identical on spend, loyalty, and satisfaction. Practical implication: in a real-world version of
this analysis, "Frequency of Purchases" and "Subscription Status" would need to be validated
against actual transaction timestamps rather than trusted as reliable loyalty signals on their
own.
"""
    )

# ========================================================================
# TAB 5 — Seasonality
# ========================================================================
with tab5:
    st.subheader("Are there seasonal shifts in category demand?")

    season_cat = pd.crosstab(df["Season"], df["Category"])
    season_order = [s for s in ["Spring", "Summer", "Fall", "Winter"] if s in season_cat.index]
    season_cat = season_cat.reindex(season_order)

    fig = px.imshow(season_cat, text_auto=True, aspect="auto",
                     title="Order Volume: Season × Category", color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

    season_rev = df.groupby("Season")["Purchase Amount (USD)"].sum().reindex(season_order).reset_index()
    fig2 = px.line(season_rev, x="Season", y="Purchase Amount (USD)", markers=True,
                   title="Total Revenue by Season")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        """
**Finding:** Category mix is remarkably stable across seasons — Clothing and Accessories
dominate order volume in every season, and Outerwear (the category one would expect to spike in
Winter) shows only a marginal seasonal bump. This flat seasonality is consistent with the dataset
being **synthetically/uniformly generated** rather than sampled from real seasonal retail demand,
where Outerwear and Footwear typically swing much more sharply between seasons.
"""
    )

# ========================================================================
# TAB 6 — Correlations
# ========================================================================
with tab6:
    st.subheader("Do numeric variables actually relate to each other?")

    num_cols = ["Age", "Purchase Amount (USD)", "Review Rating", "Previous Purchases"]
    corr = df[num_cols].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                     title="Correlation Matrix (numeric variables)")
    st.plotly_chart(fig, use_container_width=True)

    colx, coly = st.columns(2)
    x_var = colx.selectbox("X axis", num_cols, index=0)
    y_var = coly.selectbox("Y axis", num_cols, index=1)

    fig2 = px.scatter(
        df.sample(min(len(df), 1000), random_state=1),
        x=x_var,
        y=y_var,
        opacity=0.5,
        title=f"{x_var} vs {y_var}"
    )

    st.plotly_chart(fig2, use_container_width=True)

    max_corr = corr.where(~np.eye(len(corr), dtype=bool)).abs().max().max()
    st.markdown(
        f"""
**Finding:** Every pairwise correlation among Age, Purchase Amount, Review Rating, and Previous
Purchases is close to zero (strongest absolute correlation in the current filter: **{max_corr:.3f}**).
There is no meaningful linear relationship between how much a customer spends, how they rate
products, their age, or their purchase history. For an analytics/ML project this is itself an
important finding: it suggests **purchase amount here is not demographically or behaviorally
driven** (again pointing to randomized/synthetic generation), so predictive modeling on this raw
dataset would need engineered or external features to have any real signal.
"""
    )

# ========================================================================
# TAB 7 — Data Quality
# ========================================================================
with tab7:
    st.subheader("Data quality & generation-process observations")

    dq1, dq2 = st.columns(2)
    with dq1:
        st.markdown("**Missing values**")
        st.dataframe(df_raw.isnull().sum()[df_raw.isnull().sum() > 0].rename("Missing count"))
    with dq2:
        st.markdown("**Duplicate encoding check**")
        identical = (df_raw["Promo Code Used"] == df_raw["Discount Applied"]).mean() * 100
        st.metric("Promo Code Used == Discount Applied", f"{identical:.1f}% of rows")

    st.markdown(
        """
This dataset (widely used as a "Kaggle-style" synthetic retail dataset) is well suited for
practicing an **analytics workflow end-to-end** — cleaning, EDA, hypothesis testing, dashboarding
— but several patterns suggest it is **artificially generated rather than observed real-world
behavior**, which matters for how findings should be framed:

- **Review Rating** has 37 missing values (~0.9%) and no other column has missingness — an
  atypical pattern for a truly observational dataset, where missingness usually clusters with
  other fields (e.g. incomplete orders).
- **Promo Code Used** and **Discount Applied** are 100% identical row-for-row — one is a redundant
  derived copy of the other.
- **Subscription Status** is `Yes` for **0% of female customers**, which is an extreme and
  unrealistic split for any real subscription program.
- Near-zero correlations between all numeric variables (Tab 6) and near-flat seasonal demand
  (Tab 5) both indicate the "Purchase Amount" and category fields were likely assigned close to
  uniformly at random rather than through a realistic customer-behavior simulation.

**Recommendation for the project write-up:** frame the deliverable as a demonstration of
analytical method (EDA, dashboarding, hypothesis testing, and critical data-quality assessment)
rather than as a source of generalizable retail insight — and explicitly call out the anomalies
above as evidence of careful, skeptical data analysis rather than treating every pattern in the
data as a genuine business finding.
"""
    )

st.markdown("---")
st.caption("Built with Streamlit • Data: customer_shopping_behavior.csv (3,900 records)")
