import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
locale.setlocale(locale.LC_ALL, '')


# Load data
df_18 = pd.read_excel("hotel_revenue_historical_full.xlsx", sheet_name="2018")
df_19 = pd.read_excel("hotel_revenue_historical_full.xlsx", sheet_name="2019")
df_20 = pd.read_excel("hotel_revenue_historical_full.xlsx", sheet_name="2020")
df_market_segment = pd.read_excel("hotel_revenue_historical_full.xlsx", sheet_name="market_segment")
df_meal_cost = pd.read_excel("hotel_revenue_historical_full.xlsx", sheet_name="meal_cost")

df_all_year = pd.concat([df_18, df_19, df_20])

df_all_meal = pd.merge(df_all_year, df_meal_cost, on="meal")
df_all = pd.merge(df_all_meal, df_market_segment, on="market_segment")
df_all['arrival_date'] = pd.to_datetime(
    df_all['arrival_date_year'].astype(str) + '-' + df_all['arrival_date_month'] + '-' + df_all[
        'arrival_date_day_of_month'].astype(str))

# Calculate Total Revenue, Average Daily Rate, and Total Number of Stays
total_revenue = df_all['adr'].sum()
average_daily_rate = df_all['adr'].mean()
total_stays = df_all['stays_in_weekend_nights'].sum() + df_all['stays_in_week_nights'].sum()

# ADR Trends Over Time
adr_trends = df_all.groupby('arrival_date')['adr'].mean().reset_index()

# Average ADR by Year
group_df_adr_year = df_all.groupby("arrival_date_year").agg({"adr": "mean"}).reset_index()

# Required Car Parking Spaces by Year
group_df_parking_year = df_all.groupby("arrival_date_year").agg({"required_car_parking_spaces": "sum"}).reset_index()

# Average ADR by Customer Type
group_df_adr_customer = df_all.groupby("customer_type").agg({"adr": "mean"}).reset_index()

# Total Revenue by Country
group_df_country = df_all.groupby("country").agg({"adr": "sum"}).reset_index()

# Streamlit app
st.set_page_config(
    page_title="Hotel Revenue Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# Title
colT1,colT2 = st.columns([1,2])
with colT2:
    st.title("Hotel Revenue Dashboard")

st.markdown("""---""")

# Key Indicators (Side by Side)
st.subheader('Key Indicators')

key_indicators_container = st.container()

with key_indicators_container:
    col_empty, col1, col2, col3, col_empty2 = st.columns(5)

    with col1:
        st.metric(label='Total Revenue', value=f"${locale.format_string('%0.0f', total_revenue, grouping=True)}M")

    with col2:
        st.metric(label='Average Daily Rate (ADR)', value=f"${locale.format_string('%0.2f', average_daily_rate, grouping=True)}")

    with col3:
        st.metric(label='Total Number of Stays', value=f"{locale.format_string('%0.0f', total_stays, grouping=True)}")


st.markdown("""---""")

# Average ADR by Customer Type and Total Revenue by Country (Side by Side)
st.subheader('Total Revenue by Country')

col1 = st.columns(1)[0]


zmin = 0
zmax = 1000000
zmid = 500000

fig_map = go.Figure(data=go.Choropleth(
    locations=list(group_df_country["country"].unique()),
    z=list(group_df_country["adr"]),
    zmin=zmin,
    zmax=zmax,
    zmid=zmid,
    colorscale='ylgnbu',
    reversescale = False,
    marker_line_color='black',
    marker_line_width=0.5,
    colorbar_title='Count'
))

fig_map.update_layout(
    # title=dict(text='Total Revenue by Country', x=0.5, y=0.9, font=dict(size=16)),
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular',
        bgcolor='black'
    ),
    margin=dict(l=0, r=0, t=0, b=0)
)

with col1:
    col1.plotly_chart(fig_map, use_container_width=True)


st.markdown("""---""")

# Average ADR by Year and Required Car Parking Spaces by Year (Side by Side)
st.subheader('Average ADR by Year and Required Car Parking Spaces by Year')

fig_bar = go.Figure(data=[go.Bar(
    y=group_df_parking_year["required_car_parking_spaces"],
    x=group_df_parking_year["arrival_date_year"],
    marker=dict(color=group_df_parking_year["required_car_parking_spaces"], colorscale='Blues')
)])

fig_bar.update_layout(
    title=dict(text='Required Car Parking Spaces by Year', x=0.5, y=0.9, font=dict(size=16)),
    font=dict(family='Arial', size=12, color='black'),
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(title='Required Car Parking Spaces'),
    xaxis=dict(tickmode='array', tickvals=group_df_parking_year["arrival_date_year"],
               ticktext=group_df_parking_year["arrival_date_year"],
               showgrid=False, title='Year'),
)

fig_bar.update_traces(
    hoverinfo='x+y',
    texttemplate='%{y:.2f}',
    marker=dict(line=dict(color='#000000', width=1))
)

fig_bar2 = go.Figure(data=[go.Bar(
    y=group_df_adr_year["arrival_date_year"],
    x=group_df_adr_year["adr"],
    orientation='h',
    marker=dict(color=group_df_adr_year["adr"], colorscale='Blues')
)])

fig_bar2.update_layout(
    title=dict(text='Average ADR by Year', x=0.5, y=0.9, font=dict(size=16)),
    font=dict(family='Arial', size=12, color='black'),
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(title='ADR'),
    yaxis=dict(tickmode='array', tickvals=group_df_adr_year["arrival_date_year"],
               ticktext=group_df_adr_year["arrival_date_year"],
               showgrid=False, title='Year'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

fig_bar2.update_traces(
    hoverinfo='x+y',
    texttemplate='%{x:.2f}',  # Round to two decimal places
    marker=dict(line=dict(color='#000000', width=1))
)

col1, col2 = st.columns(2)

with col1:
    col1.plotly_chart(fig_bar, use_container_width=True)

with col2:
    col2.plotly_chart(fig_bar2, use_container_width=True)


# ADR Trends Over Time

fig_pie = go.Figure(data=[go.Pie(
    labels=group_df_adr_customer["customer_type"],
    values=group_df_adr_customer["adr"],
    hole=0.4
)])

fig_pie.update_layout(
    title=dict(text='Average ADR by Customer Type', x=0.5, y=0.9, font=dict(size=16)),
    font=dict(family='Arial', size=12, color='black'),
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

fig_pie.update_traces(
    hoverinfo='label+percent',
    textinfo='value',
    textfont_size=20,
    texttemplate='%{value:.2f}',
    marker=dict(
        line=dict(color='#000000', width=2)
    )
)

st.markdown("""---""")
st.subheader('Average Daily Rate (ADR) Trends Over Time and Average ADR by Customer Type')

col1, col2 = st.columns(2)

with col1:
    col1.plotly_chart(px.line(adr_trends, x='arrival_date', y='adr', title='Average Daily Rate (ADR) Trends Over Time'))

with col2:
    col2.plotly_chart(fig_pie, use_container_width=True)




