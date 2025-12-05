"""Utility functions for the drought monitoring dashboard"""
import json
import numpy as np
import plotly.graph_objects as go

# SPEI category definitions
SPEI_CATEGORIES = [
    ("Extreme", '#8B0000', '🔴'),
    ("Severe", '#FF4500', '🟠'),
    ("Moderate", '#FFA500', '🟡'),
    ("Mild", '#FFD700', '🟡'),
    ("Normal", '#90EE90', '🟢'),
    ("Wet", '#00FF00', '🔵'),
    ("Very Wet", '#0000FF', '🔵')
]


def create_region_slices(ds, region):
    """Create lat/lon slices based on data ordering and region bounds"""
    lat_ascending = ds.lat[0] < ds.lat[-1]
    lon_ascending = ds.lon[0] < ds.lon[-1]

    if lat_ascending:
        lat_slice = slice(region["lat"][0], region["lat"][1])
    else:
        lat_slice = slice(region["lat"][1], region["lat"][0])

    if lon_ascending:
        lon_slice = slice(region["lon"][0], region["lon"][1])
    else:
        lon_slice = slice(region["lon"][1], region["lon"][0])

    return lat_slice, lon_slice


def load_continents():
    """Load continent data from JSON file"""
    with open('data/continents.json', 'r') as f:
        return json.load(f)


def get_regions_dict():
    """Build regions dictionary from continents data plus additional regions"""
    continents = load_continents()
    regions = {
        "Global": {"lat": [-90, 90], "lon": [-180, 180]},
        "Australia": {"lat": [-45, -10], "lon": [110, 155]},
    }
    # Add continent regions
    for continent_name, continent_data in continents.items():
        regions[continent_name] = continent_data["region"]
    return regions


def load_country_centroids():
    """Load country centroid coordinates from JSON file"""
    with open('data/country_centroids.json', 'r') as f:
        return json.load(f)


def get_country_centroids(continent_name):
    """Returns country centroids for a specific continent"""
    all_centroids = load_country_centroids()
    centroids = all_centroids.get(continent_name, {})
    # Convert lists back to tuples for compatibility
    return {country: tuple(coords) for country, coords in centroids.items()}


def spei_to_color(spei_val):
    """Convert SPEI value to color code"""
    if spei_val < -2:
        return '#8B0000'  # Extreme drought
    elif spei_val < -1.5:
        return '#FF4500'  # Severe drought
    elif spei_val < -1:
        return '#FFA500'  # Moderate drought
    elif spei_val < -0.5:
        return '#FFD700'  # Mild drought
    elif spei_val < 0.5:
        return '#90EE90'  # Normal
    elif spei_val < 1:
        return '#00FF00'  # Slightly wet
    elif spei_val < 1.5:
        return '#00CED1'  # Wet
    else:
        return '#0000FF'  # Very wet


def get_legend_traces():
    """Returns standard legend traces for SPEI maps"""
    legend_data = [
        ('Extreme Drought', '#8B0000'),
        ('Severe Drought', '#FF4500'),
        ('Moderate Drought', '#FFA500'),
        ('Mild Drought', '#FFD700'),
        ('Normal', '#90EE90'),
        ('Wet', '#00FF00'),
        ('Very Wet', '#0000FF')
    ]

    traces = []
    for label, color in legend_data:
        traces.append(go.Scattermapbox(
            lat=[None],
            lon=[None],
            mode='markers',
            marker=dict(size=15, color=color),
            name=label,
            showlegend=True
        ))
    return traces


def categorize_spei(spei_val):
    """Categorize SPEI value into drought severity levels"""
    if np.isnan(spei_val):
        return 4  # default to normal
    if spei_val < -2:
        return 0  # Extreme Drought
    elif spei_val < -1.5:
        return 1  # Severe Drought
    elif spei_val < -1:
        return 2  # Moderate Drought
    elif spei_val < -0.5:
        return 3  # Mild Drought
    elif spei_val <= 0.5:
        return 4  # Normal
    elif spei_val <= 1.5:
        return 5  # Wet
    else:
        return 6  # Very Wet


def calculate_category_count(spei_values, category_idx):
    """Calculate count of values in a specific SPEI category"""
    thresholds = [
        (lambda v: v < -2),                                    # 0: Extreme
        (lambda v: (v >= -2) & (v < -1.5)),                   # 1: Severe
        (lambda v: (v >= -1.5) & (v < -1)),                   # 2: Moderate
        (lambda v: (v >= -1) & (v < -0.5)),                   # 3: Mild
        (lambda v: (v >= -0.5) & (v <= 0.5)),                 # 4: Normal
        (lambda v: (v > 0.5) & (v <= 1.5)),                   # 5: Wet
        (lambda v: v > 1.5)                                    # 6: Very Wet
    ]
    return np.sum(thresholds[category_idx](spei_values))


def get_region_spei_values(spei_data, lat, lon, grid_size=5):
    """Get all SPEI values in a region around a coordinate

    Args:
        spei_data: xarray dataset with SPEI values
        lat: latitude coordinate
        lon: longitude coordinate
        grid_size: size of grid to sample (default 5 for 5x5, use larger for big regions)

    Returns:
        Array of valid SPEI values in the region (NaN values removed)
    """
    try:
        # Find nearest grid points
        lat_idx = np.abs(spei_data.lat.values - lat).argmin()
        lon_idx = np.abs(spei_data.lon.values - lon).argmin()

        # Sample a grid around the point
        half_size = grid_size // 2
        lat_start = max(0, lat_idx - half_size)
        lat_end = min(len(spei_data.lat), lat_idx + half_size + 1)
        lon_start = max(0, lon_idx - half_size)
        lon_end = min(len(spei_data.lon), lon_idx + half_size + 1)

        # Get values from the region
        region_values = spei_data.values[lat_start:lat_end, lon_start:lon_end]
        valid_values = region_values[~np.isnan(region_values)]

        return valid_values
    except:
        return np.array([])


def get_spei_at_location(spei_data, lat, lon, grid_size=5):
    """Get average SPEI value in a region around a coordinate

    Args:
        spei_data: xarray dataset with SPEI values
        lat: latitude coordinate
        lon: longitude coordinate
        grid_size: size of grid to sample (default 5 for 5x5, use larger for big regions)
    """
    valid_values = get_region_spei_values(spei_data, lat, lon, grid_size)
    if len(valid_values) > 0:
        return np.mean(valid_values)
    else:
        return np.nan


def prepare_mapbox_data(spei_region_data):
    """Prepare SPEI data for Mapbox visualization

    Args:
        spei_region_data: xarray DataArray with SPEI values

    Returns:
        Tuple of (lats_clean, lons_clean, spei_clean) with NaN values removed
    """
    # Create meshgrid
    lons, lats = np.meshgrid(spei_region_data.lon.values, spei_region_data.lat.values)
    lons_flat = lons.flatten()
    lats_flat = lats.flatten()
    spei_flat = spei_region_data.values.flatten()

    # Remove NaN values
    mask = ~np.isnan(spei_flat)
    lons_clean = lons_flat[mask]
    lats_clean = lats_flat[mask]
    spei_clean = spei_flat[mask]

    return lats_clean, lons_clean, spei_clean


def create_mapbox_figure(lats, lons, spei_values, mapbox_token, center_lat, center_lon, zoom, title, marker_size=8, opacity=0.3):
    """Create a standardized Mapbox figure with SPEI data"""
    fig = go.Figure()

    # Convert SPEI values to colors
    colors = [spei_to_color(val) for val in spei_values]

    # Add scatter points
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(
            size=marker_size,
            color=colors,
            opacity=opacity
        ),
        text=[f'SPEI: {val:.2f}' for val in spei_values],
        hovertemplate='<b>%{text}</b><br>Lat: %{lat:.2f}<br>Lon: %{lon:.2f}<extra></extra>',
        name='Drought Data',
        showlegend=False
    ))

    # Add legend traces
    for trace in get_legend_traces():
        fig.add_trace(trace)

    # Update layout
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,
            style='mapbox://styles/mapbox/dark-v11',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom
        ),
        height=700 if 'Global' in title else 600,
        margin=dict(l=0, r=0, t=40 if 'Global' in title else 20, b=0),
        title=dict(
            text=title,
            font=dict(size=20, family='Geist', color='white')
        ) if 'Global' in title else None,
        legend=dict(
            font=dict(size=14, family='Geist'),
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.3)',
            borderwidth=1
        ),
        hovermode='closest',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    return fig


def find_nearest_time_index(time_values, target_date):
    """Find the index of the nearest time value to target_date"""
    time_diffs = np.abs([(tv - target_date).days for tv in time_values])
    return int(np.argmin(time_diffs))
