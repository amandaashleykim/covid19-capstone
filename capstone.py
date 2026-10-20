import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard title
st.title("COVID-19 Global Trends Dashboard")

# Description
st.write(
    "Explore and compare daily and cumulative COVID-19 "
    "cases across countries from January 2020 to March 2023."
)

# Data source
st.caption("Data source: Johns Hopkins University CSSE COVID-19 Dataset")

# Load the COVID-19 dataset
covid = pd.read_csv("covid_dashboard.csv.gz")

# Display basic dataset information
st.subheader("Dataset Overview")

st.write("Number of countries:", covid["Country"].nunique())

st.write("Number of observations:", len(covid))

# Display the first five rows
st.dataframe(covid.head())

# Country selection
st.subheader("Select Countries")

# Create a list of available countries
country_list = sorted(covid["Country"].unique())

# Allow users to select multiple countries
selected_countries = st.multiselect(
    "Choose countries to compare:",
    options=country_list,
    default=["US"]
)

# Filter the dataset to selected countries
filtered_data = covid[
    covid["Country"].isin(selected_countries)
]

# Display selected countries
st.write("Selected countries:", ", ".join(selected_countries))

# Allow users to select daily or cumulative cases
st.subheader("Select Case Type")

case_type = st.radio(
    "Which COVID-19 case counts would you like to view?",
    ["Daily Cases", "Cumulative Cases"]
)

# Identify the corresponding column in the dataset
if case_type == "Daily Cases":
    selected_column = "Daily_Cases"
else:
    selected_column = "Cumulative_Cases"

# Display the selected option
st.write("Currently displaying:", case_type)

# Interactive COVID-19 line graph
st.subheader("COVID-19 Trends Over Time")

# Convert the Date column to datetime
filtered_data = filtered_data.copy()
filtered_data["Date"] = pd.to_datetime(filtered_data["Date"])

# Allow users to select a date range
st.write("Select a date range:")

start_date = st.date_input(
    "Start Date",
    value=pd.to_datetime("2020-01-22"),
    min_value=pd.to_datetime("2020-01-22"),
    max_value=pd.to_datetime("2023-03-09")
)

end_date = st.date_input(
    "End Date",
    value=pd.to_datetime("2023-03-09"),
    min_value=pd.to_datetime("2020-01-22"),
    max_value=pd.to_datetime("2023-03-09")
)

# Filter data based on selected dates
filtered_data = filtered_data[
    (filtered_data["Date"] >= pd.Timestamp(start_date)) &
    (filtered_data["Date"] <= pd.Timestamp(end_date))
]

# Create the graph if at least one country is selected
if selected_countries:

    fig = px.line(
        filtered_data,
        x="Date",
        y=selected_column,
        color="Country",
        title=f"{case_type} by Country",
        labels={
            "Date": "Date",
            selected_column: "Number of Cases",
            "Country": "Country"
        }
    )

    # Improve the graph's appearance
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Number of Cases"
    )

    # Display the graph
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Please select at least one country to display the graph.")

# Summary statistics
st.subheader("COVID-19 Summary Statistics")

if selected_countries and not filtered_data.empty:

    # Get the latest cumulative count for each selected country
    latest_cases = (
        filtered_data.sort_values("Date")
        .groupby("Country")["Cumulative_Cases"]
        .last()
        .sum()
    )

    # Calculate the net change in cumulative cases
    period_cases = (
        filtered_data.sort_values("Date")
        .groupby("Country")["Cumulative_Cases"]
        .agg(lambda x: x.iloc[-1] - x.iloc[0])
        .sum()
    )

    # Create three columns for summary statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Countries Selected", len(selected_countries))

    with col2:
        st.metric("Total Confirmed Cases", f"{latest_cases:,.0f}")

    with col3:
        st.metric("Cases During Period", f"{period_cases:,.0f}")

else:
    st.info("Select at least one country to view summary statistics.")


# Data source and limitations
st.divider()

with st.expander("About the Data and Limitations"):

    st.write("""
    **Data Source**

    This dashboard uses publicly available COVID-19 case data
    from the Johns Hopkins University Center for Systems Science
    and Engineering (JHU CSSE).

    The dataset includes 201 countries and territories,
    covering January 22, 2020, through March 9, 2023.

    **Data Processing**

    - Provincial and regional records were aggregated to
      produce country-level totals.
    - Daily cases were calculated by subtracting the previous
      day's cumulative count from the current day's count.
    - Negative daily counts resulting from reporting corrections
      were replaced with zero for visualization purposes.
    - Original cumulative counts were preserved.

    **Limitations**

    - Reported cases may underestimate actual infections
      because of differences in testing and surveillance.
    - Reporting practices varied across countries and over time.
    - Some countries reported cases in batches, creating
      artificial spikes in daily counts.
    - Replacing negative daily values with zero means adjusted
      daily totals may differ from changes in cumulative cases.
    - The dataset ends on March 9, 2023, and does not represent
      current COVID-19 surveillance.
    """)