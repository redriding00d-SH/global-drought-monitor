import streamlit as st
import xarray as xr
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
from utils import (
    load_continents, get_country_centroids,
    categorize_spei, get_region_spei_values,
    create_mapbox_figure, find_nearest_time_index,
    create_region_slices, get_regions_dict,
    calculate_category_count, SPEI_CATEGORIES,
    prepare_mapbox_data
)

# Page configuration
st.set_page_config(
    page_title="Global Drought Monitoring Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and apply custom font

def load_font():
    with open("assets/fonts/Geist-VariableFont_wght.ttf", "rb") as f:
        font_data = base64.b64encode(f.read()).decode()
    return font_data

font_base64 = load_font()

# Load Material Icons font
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
""", unsafe_allow_html=True)

# Custom CSS with Geist font and optimizations
st.markdown(f"""
<style>
    @font-face {{
        font-family: 'Geist';
        src: url(data:font/truetype;charset=utf-8;base64,{font_base64}) format('truetype');
        font-weight: 100 900;
        font-style: normal;
        font-display: swap;
    }}

    /* Global font application */
    * {{
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }}

    /* Preserve Material Icons for Streamlit UI elements - CRITICAL for deployment */
    button[kind="header"],
    button[kind="header"] span,
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] span,
    [class*="st-emotion-cache"] > span,
    span[data-baseweb="icon"],
    .material-icons,
    .material-icons-outlined {{
        font-family: 'Material Icons', 'Material Icons Outlined', sans-serif !important;
        font-feature-settings: 'liga' !important;
        -webkit-font-feature-settings: 'liga' !important;
        text-rendering: optimizeLegibility !important;
    }}

    /* Custom headers */
    .main-header {{
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }}

    .sub-header {{
        font-size: 1.2rem;
        font-weight: 400;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.01em;
    }}

    /* Headings and text elements */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 600;
        letter-spacing: -0.02em;
    }}

    [data-testid="stMetricLabel"] {{ font-weight: 500; }}
    [data-testid="stMetricValue"] {{ font-weight: 600; }}
    button, .stButton button {{ font-weight: 500; }}

    /* Tabs styling */
    [data-baseweb="tab"],
    [data-baseweb="tab"] button,
    [data-baseweb="tab"] button div,
    [data-baseweb="tab"] p {{
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }}

    [data-baseweb="tab"] p {{ margin: 0 !important; }}

    /* Custom div font size */
    div.st-emotion-cache-q8sbsg {{
        font-size: 30px !important;
    }}
</style>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_resource
def load_drought_data():
    """Load the SPEI drought dataset"""
    ds = xr.open_dataset("data/spei01.nc", engine="h5netcdf")
    return ds

# Main title
st.markdown('<h1 class="main-header">🌍 Global Drought Monitoring Dashboard</h1>', unsafe_allow_html=True)
st.markdown('''
<p class="sub-header">Interactive analysis of historical drought patterns using SPEI (Standardized Precipitation Evapotranspiration Index)</p>
<p style="text-align: center; color: #888; font-size: 0.9rem; margin-top: -1rem; margin-bottom: 1.5rem;">
SPEIbase v2.10 (Jan 1901 - Dec 2023) | Source: CRU TS 4.08 | Note: Climate datasets have a lag time of several months for quality control. 2024 data pending official release.
</p>
''', unsafe_allow_html=True)

# Load data with error handling
try:
    with st.spinner("Loading drought data..."):
        ds = load_drought_data()

    # Get time values for controls
    time_values = pd.to_datetime(ds.time.values)
    available_months_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    available_years = sorted(set([t.year for t in time_values]))

    # Default to last date in dataset
    default_month_idx = time_values[-1].month - 1
    default_year_idx = available_years.index(time_values[-1].year)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")

# Time selection in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Time Selection")

# Date selection
col1, col2 = st.sidebar.columns(2)
with col1:
    selected_month = st.selectbox(
        "Month",
        available_months_abbr,
        index=default_month_idx,
        key="selected_month"
    )
with col2:
    selected_year = st.selectbox(
        "Year",
        available_years,
        index=default_year_idx,
        key="selected_year"
    )

# Find the time index for the selected date
# Use day=16 to match the dataset's date format
selected_date = pd.Timestamp(year=selected_year, month=available_months_abbr.index(selected_month) + 1, day=16)

# Find closest available date using utility function
time_idx = find_nearest_time_index(time_values, selected_date)
selected_time = time_values[time_idx]

# Show selected date in main area with styled sidebar pointer
date_text = selected_time.strftime('%B %Y')
st.markdown(f"""
<div style="border: 1px solid #444; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span style="font-size: 1rem;">📅 <strong>Selected Date:</strong> {date_text}</span>
        </div>
        <div style="border: 1px solid #666; padding: 0.4rem 0.8rem; border-radius: 0.3rem; cursor: pointer;">
            <span style="font-size: 0.9rem; color: #aaa;">⬅️ Change in sidebar</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Region selection
st.sidebar.markdown("---")
st.sidebar.subheader("🗺️ Region Selection")

region_preset = st.sidebar.selectbox(
    "Choose a region",
    ["Global", "North America", "Europe", "Asia", "Africa", "South America", "Australia", "Custom"]
)

# Get region coordinates
regions = get_regions_dict()

if region_preset == "Custom":
    lat_min = st.sidebar.number_input("Min Latitude", -90.0, 90.0, -90.0)
    lat_max = st.sidebar.number_input("Max Latitude", -90.0, 90.0, 90.0)
    lon_min = st.sidebar.number_input("Min Longitude", -180.0, 180.0, -180.0)
    lon_max = st.sidebar.number_input("Max Longitude", -180.0, 180.0, 180.0)
    selected_region = {"lat": [lat_min, lat_max], "lon": [lon_min, lon_max]}
else:
    selected_region = regions[region_preset]

# Extract data for selected time and region
spei_data = ds['spei'].isel(time=time_idx)
lat_slice, lon_slice = create_region_slices(ds, selected_region)
spei_region = spei_data.sel(lat=lat_slice, lon=lon_slice)

# Debug: Check data structure
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Info:**")
st.sidebar.text(f"Lat range: {float(ds.lat.min()):.1f} to {float(ds.lat.max()):.1f}")
st.sidebar.text(f"Lon range: {float(ds.lon.min()):.1f} to {float(ds.lon.max()):.1f}")
st.sidebar.text(f"Time: {selected_time.strftime('%Y-%m')}")

# Show selected region size
st.sidebar.text(f"Region size: {len(spei_region.lat)} x {len(spei_region.lon)}")

# Load continental data from JSON
CONTINENTS = load_continents()

# Tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗺️ Global Map",
    "🌍 Africa",
    "🌎 North America",
    "🌏 Asia",
    "🇪🇺 Europe",
    "🌎 South America",
    "🌏 Australia"
])

with tab1:
    # Get Mapbox token from secrets
    try:
        mapbox_token = st.secrets["MAPBOX_TOKEN"]
    except:
        st.error("⚠️ Mapbox token not found. Please add it to `.streamlit/secrets.toml`")
        mapbox_token = None

    if mapbox_token and mapbox_token != "your_mapbox_token_here":
        # Prepare data for Mapbox
        lats_clean, lons_clean, spei_clean = prepare_mapbox_data(spei_region)

        if len(spei_clean) > 0:
            # Calculate map center and zoom
            center_lat = np.mean([selected_region["lat"][0], selected_region["lat"][1]])
            center_lon = np.mean([selected_region["lon"][0], selected_region["lon"][1]])

            # Adjust zoom based on region size
            lat_range = abs(selected_region["lat"][1] - selected_region["lat"][0])
            lon_range = abs(selected_region["lon"][1] - selected_region["lon"][0])
            max_range = max(lat_range, lon_range)

            # Calculate zoom level (approximate)
            if max_range > 120:
                zoom = 1
            elif max_range > 60:
                zoom = 2
            elif max_range > 30:
                zoom = 3
            else:
                zoom = 4

            # Create map using utility function
            fig = create_mapbox_figure(
                lats_clean, lons_clean, spei_clean,
                mapbox_token, center_lat, center_lon, zoom,
                f"SPEI Drought Index - {region_preset}"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No valid data for this region and time period")
    else:
        # Fallback to basic heatmap if no token
        st.warning("🗺️ Add your Mapbox token to `.streamlit/secrets.toml` for the professional map view")

        fig = go.Figure(data=go.Heatmap(
            z=spei_region.values,
            x=spei_region.lon.values,
            y=spei_region.lat.values,
            colorscale=[
                [0, '#8B0000'], [0.25, '#FF4500'], [0.4, '#FFA500'],
                [0.5, '#FFFF00'], [0.6, '#90EE90'], [0.75, '#00FF00'], [1, '#0000FF']
            ],
            zmid=0, zmin=-3, zmax=3,
            colorbar=dict(
                title="SPEI Index",
                tickvals=[-3, -2, -1, 0, 1, 2, 3],
                ticktext=['Extreme Drought', 'Severe', 'Moderate', 'Normal', 'Wet', 'Very Wet', 'Extremely Wet']
            )
        ))
        fig.update_layout(
            title=f"SPEI Drought Index - {region_preset}",
            xaxis_title="Longitude", yaxis_title="Latitude",
            height=600, hovermode='closest'
        )
        st.plotly_chart(fig, use_container_width=True)

    # SPEI interpretation guide
    with st.expander("📖 How to interpret SPEI values"):
        st.markdown("""
        **SPEI (Standardized Precipitation Evapotranspiration Index)** measures drought severity:

        | SPEI Value | Category | Color |
        |------------|----------|-------|
        | < -2.0 | Extreme Drought | Dark Red |
        | -2.0 to -1.5 | Severe Drought | Red |
        | -1.5 to -1.0 | Moderate Drought | Orange |
        | -1.0 to 1.0 | Normal Conditions | Yellow/Green |
        | 1.0 to 1.5 | Moderately Wet | Light Blue |
        | 1.5 to 2.0 | Very Wet | Blue |
        | > 2.0 | Extremely Wet | Dark Blue |
        """)

# Helper function to render continental map and data
def render_continental_view(continent_name, continent_data, ds, time_idx, selected_time, mapbox_token):
    st.subheader(f"{continent_name} - {selected_time.strftime('%B %Y')}")

    # Get continental region and extract data
    cont_region = continent_data["region"]
    spei_data_cont = ds['spei'].isel(time=time_idx)
    lat_slice, lon_slice = create_region_slices(ds, cont_region)
    spei_cont = spei_data_cont.sel(lat=lat_slice, lon=lon_slice)

    # Calculate continental statistics
    valid_data = spei_cont.values[~np.isnan(spei_cont.values)]

    if len(valid_data) > 0:
        # Use category counting function for consistency
        extreme_drought_pct = (calculate_category_count(spei_cont.values, 0) / len(valid_data)) * 100
        severe_moderate_drought_pct = ((calculate_category_count(spei_cont.values, 1) +
                                        calculate_category_count(spei_cont.values, 2)) / len(valid_data)) * 100
        normal_pct = (calculate_category_count(spei_cont.values, 4) / len(valid_data)) * 100
        wet_pct = ((calculate_category_count(spei_cont.values, 5) +
                    calculate_category_count(spei_cont.values, 6)) / len(valid_data)) * 100

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔥 Extreme Drought", f"{extreme_drought_pct:.1f}%")
        with col2:
            st.metric("⚠️ Severe-Moderate Drought", f"{severe_moderate_drought_pct:.1f}%")
        with col3:
            st.metric("✅ Normal", f"{normal_pct:.1f}%")
        with col4:
            st.metric("💧 Wet", f"{wet_pct:.1f}%")

        st.markdown("---")

        # Render map
        if mapbox_token and mapbox_token != "your_mapbox_token_here":
            # Prepare data
            lats_clean, lons_clean, spei_clean = prepare_mapbox_data(spei_cont)

            if len(spei_clean) > 0:
                center_lat = np.mean(cont_region["lat"])
                center_lon = np.mean(cont_region["lon"])

                # Create map using utility function
                fig = create_mapbox_figure(
                    lats_clean, lons_clean, spei_clean,
                    mapbox_token, center_lat, center_lon, 3,
                    continent_name, marker_size=6, opacity=0.7
                )

                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Countries/States grouped by drought severity
        label = "State" if continent_name == "Australia" else "Country"
        st.subheader(f"📍 Drought Severity by {label}")

        # Get country centroids for this continent
        country_centroids = get_country_centroids(continent_name)

        # Categorize countries/states by drought severity
        # Australia: uses average SPEI (states are huge)
        # Other continents: uses dominant category (most common condition)
        countries = continent_data["countries"]
        country_categories = {i: [] for i in range(7)}

        for country in countries:
            if country in country_centroids:
                lat, lon = country_centroids[country]
                # Use larger sampling grid for Australian states (they're huge!)
                grid_size = 50 if continent_name == "Australia" else 5

                # Get SPEI values in the country's region
                valid_values = get_region_spei_values(spei_cont, lat, lon, grid_size)

                if len(valid_values) > 0:
                    if continent_name == "Australia":
                        # For Australian states, use AVERAGE SPEI (states are too large for dominant category)
                        avg_spei = np.mean(valid_values)
                        category = categorize_spei(avg_spei)
                        country_categories[category].append(country)
                    else:
                        # For other countries, use DOMINANT category (most common)
                        categorized = np.array([categorize_spei(v) for v in valid_values])

                        # Count occurrences of each category
                        category_counts = np.bincount(categorized, minlength=7)

                        # Assign country to the category with the most occurrences
                        dominant_category = np.argmax(category_counts)
                        country_categories[dominant_category].append(country)
                else:
                    # No valid data, use continental mean as fallback
                    category = categorize_spei(np.nanmean(spei_cont.values))
                    country_categories[category].append(country)
            else:
                # If no centroid, use continental mean
                continent_mean = np.nanmean(spei_cont.values)
                category = categorize_spei(continent_mean)
                country_categories[category].append(country)

        # Create 7 columns for each category
        cols = st.columns(7)

        # Calculate percentages for each category
        total_points = len(valid_data)
        for idx, (label, color, dot) in enumerate(SPEI_CATEGORIES):
            with cols[idx]:
                st.markdown(f"<div style='font-size: 16px; font-weight: 600; margin-bottom: 10px;'>{dot} {label}</div>", unsafe_allow_html=True)

                # Calculate percentage of region in this category
                cat_count = calculate_category_count(spei_cont.values, idx)
                pct = (cat_count / total_points * 100) if total_points > 0 else 0
                st.markdown(f"<div style='font-size: 18px; font-weight: 600; margin-bottom: 15px; color: {color};'>{pct:.1f}%</div>", unsafe_allow_html=True)

                st.markdown("---")

                # Show countries in this category
                countries_in_cat = country_categories.get(idx, [])
                if countries_in_cat:
                    for country in countries_in_cat:
                        st.markdown(f"<div style='font-size: 15px; line-height: 1.8; font-weight: 500; margin-bottom: 4px;'>• {country}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-size: 13px; color: #888; font-style: italic; margin-top: 10px;'>No countries</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Data table
        st.subheader("📊 Regional Statistics")

        # Use valid_data for statistics to avoid warnings
        if len(valid_data) > 0:
            stats_df = pd.DataFrame({
                "Metric": ["Mean SPEI", "Median SPEI", "Std Dev", "Min SPEI", "Max SPEI"],
                "Value": [
                    f"{np.mean(valid_data):.3f}",
                    f"{np.median(valid_data):.3f}",
                    f"{np.std(valid_data):.3f}",
                    f"{np.min(valid_data):.3f}",
                    f"{np.max(valid_data):.3f}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        else:
            st.info("No valid data available for statistics.")
    else:
        st.warning("⚠️ No valid data for this continent in the selected time period.")

# Render each continental tab
with tab2:
    render_continental_view("Africa", CONTINENTS["Africa"], ds, time_idx, selected_time, mapbox_token)

with tab3:
    render_continental_view("North America", CONTINENTS["North America"], ds, time_idx, selected_time, mapbox_token)

with tab4:
    render_continental_view("Asia", CONTINENTS["Asia"], ds, time_idx, selected_time, mapbox_token)

with tab5:
    render_continental_view("Europe", CONTINENTS["Europe"], ds, time_idx, selected_time, mapbox_token)

with tab6:
    render_continental_view("South America", CONTINENTS["South America"], ds, time_idx, selected_time, mapbox_token)

with tab7:
    render_continental_view("Australia", CONTINENTS["Australia"], ds, time_idx, selected_time, mapbox_token)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Global Drought Monitoring Dashboard | Data: SPEI Dataset | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
