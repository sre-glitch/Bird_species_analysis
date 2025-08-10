import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("cleaned_bird_data.csv")

# Sidebar filters
st.sidebar.title("Filter Options")
habitat = st.sidebar.multiselect("Select Habitat", options=df["Habitat"].unique(), default=df["Habitat"].unique())
season = st.sidebar.multiselect("Select Season", options=df["Season"].unique(), default=df["Season"].unique())

# Filtered dataset
filtered_df = df[(df["Habitat"].isin(habitat)) & (df["Season"].isin(season))]

st.title("Bird Species Observation Dashboard")

# 1. Unique species by habitat
species_habitat = filtered_df.groupby("Habitat")["Scientific_Name"].nunique().reset_index()
fig1 = px.bar(species_habitat, x="Habitat", y="Scientific_Name", title="Unique Species by Habitat",
              labels={"Scientific_Name": "Unique Species Count"})
st.plotly_chart(fig1)

# 2. Heatmap of observations
heat_df = filtered_df.groupby(["Year", "Month"]).size().reset_index(name="Observations")
fig2 = px.density_heatmap(heat_df, x="Month", y="Year", z="Observations", color_continuous_scale="Viridis",
                          title="Observation Density (Year vs Month)")
st.plotly_chart(fig2)

# 3. Bubble chart: Temperature vs Humidity
env_df = filtered_df.dropna(subset=["Temperature", "Humidity", "Initial_Three_Min_Cnt"])
env_df['Initial_Three_Min_Cnt'] = pd.to_numeric(env_df['Initial_Three_Min_Cnt'], errors='coerce')
env_df = env_df[env_df['Initial_Three_Min_Cnt'].notnull()]
scaled_size = env_df["Initial_Three_Min_Cnt"] * 2
fig3 = px.scatter(env_df, x="Temperature", y="Humidity", size=scaled_size, color="Habitat",
                  hover_data=["Scientific_Name"], title="Temperature vs Humidity vs Bird Activity")
st.plotly_chart(fig3)

# 4. Top 10 Observed Species
top_species = filtered_df["Scientific_Name"].value_counts().nlargest(10).reset_index()
top_species.columns = ["Scientific_Name", "Observations"]
fig4 = px.bar(top_species, x="Scientific_Name", y="Observations", title="Top 10 Observed Species")
st.plotly_chart(fig4)

# 5. Seasonal distribution for selected species
species_select = st.selectbox("Explore Specific Species", df["Scientific_Name"].dropna().unique())
species_df = filtered_df[filtered_df["Scientific_Name"] == species_select]
fig5 = px.histogram(species_df, x="Season", color="Habitat", title=f"Seasonal Distribution of {species_select}")
st.plotly_chart(fig5)

# 6. Yearly total bird observations (cleaned & fixed)
yearly_obs = (
    filtered_df
    .dropna(subset=["Year"])
    .loc[filtered_df["Year"].between(1900, 2100)]  # Filter valid years
    .assign(Year=lambda x: x["Year"].astype(int))
    .groupby("Year")
    .size()
    .reset_index(name="Observations")
    .sort_values("Year")
)

fig6 = px.bar(
    yearly_obs,
    x="Year",
    y="Observations",
    title="Yearly Bird Observations (All Records)",
    text="Observations"
)
fig6.update_traces(textposition="outside")
st.plotly_chart(fig6)


# 7. Monthly species diversity
monthly_diversity = filtered_df.groupby("Month")["Scientific_Name"].nunique().reset_index()
fig7 = px.bar(monthly_diversity, x="Month", y="Scientific_Name",
              title="Monthly Unique Species Count", labels={"Scientific_Name": "Unique Species"})
st.plotly_chart(fig7)

# 8. Sex ratio distribution
sex_counts = filtered_df["Sex"].value_counts().reset_index()
sex_counts.columns = ["Sex", "Count"]
fig8 = px.pie(sex_counts, names="Sex", values="Count", title="Sex Ratio of Observations")
st.plotly_chart(fig8)

# 9. Most common identification methods
id_method_counts = filtered_df["ID_Method"].value_counts().reset_index()
id_method_counts.columns = ["ID_Method", "Count"]
fig9 = px.bar(id_method_counts, x="ID_Method", y="Count", title="Most Common Identification Methods")
st.plotly_chart(fig9)

# 10. Distance vs Average Bird Count
dist_count = filtered_df.groupby("Distance")["Initial_Three_Min_Cnt"].mean().reset_index()
fig10 = px.bar(dist_count, x="Distance", y="Initial_Three_Min_Cnt",
               title="Average Bird Count by Observation Distance")
st.plotly_chart(fig10)

# 11. Observer activity (Top 10 observers)
observer_activity = filtered_df["Observer"].value_counts().nlargest(10).reset_index()
observer_activity.columns = ["Observer", "Observations"]
fig11 = px.bar(observer_activity, x="Observer", y="Observations", title="Top 10 Observers")
st.plotly_chart(fig11)

# 12. Watchlist species count by habitat
watchlist_counts = filtered_df[filtered_df["PIF_Watchlist_Status"] == True].groupby("Habitat")["Scientific_Name"].nunique().reset_index()
fig12 = px.bar(watchlist_counts, x="Habitat", y="Scientific_Name", title="Watchlist Species Count by Habitat",
               labels={"Scientific_Name": "Unique Watchlist Species"})
st.plotly_chart(fig12)

# 13. Monthly flyover observation rate
flyover_rate = filtered_df.groupby("Month")["Flyover_Observed"].mean().reset_index()
fig13 = px.line(flyover_rate, x="Month", y="Flyover_Observed", title="Monthly Flyover Observation Rate")
st.plotly_chart(fig13)

# 14. High-activity regions & seasons for selected species
st.subheader("High-Activity Regions & Seasons for Selected Species")
species_select_region = st.selectbox("Choose a species to analyze activity regions", df["Scientific_Name"].dropna().unique(), key="region_species")
species_region_df = filtered_df[filtered_df["Scientific_Name"] == species_select_region]

# Group by Plot and Season for observation counts
region_season_counts = species_region_df.groupby(["Plot_Name", "Season"]).size().reset_index(name="Observations")
fig14 = px.bar(region_season_counts, x="Plot_Name", y="Observations", color="Season",
               title=f"High-Activity Regions & Seasons for {species_select_region}")
st.plotly_chart(fig14)

# 15. Environmental factors influencing bird activity
st.subheader("Environmental Factors and Bird Activity")
env_factors = filtered_df.dropna(subset=["Temperature", "Humidity", "Initial_Three_Min_Cnt"])
env_factors_grouped = env_factors.groupby(["Temperature", "Humidity"])["Initial_Three_Min_Cnt"].mean().reset_index()
fig15 = px.scatter(env_factors_grouped, x="Temperature", y="Humidity", size="Initial_Three_Min_Cnt",
                   title="Environmental Factors Influencing Bird Activity",
                   labels={"Initial_Three_Min_Cnt": "Avg Bird Count"})
st.plotly_chart(fig15)

# 16. At-risk species & conservation priorities
st.subheader("At-Risk Species & Conservation Priorities")
at_risk_species = filtered_df[filtered_df["PIF_Watchlist_Status"] == True]["Scientific_Name"].value_counts().reset_index()
at_risk_species.columns = ["Scientific_Name", "Observations"]
fig16 = px.bar(at_risk_species, x="Scientific_Name", y="Observations",
               title="At-Risk Species (PIF Watchlist)", color="Observations")
st.plotly_chart(fig16)
