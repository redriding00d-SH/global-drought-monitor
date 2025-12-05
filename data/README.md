# Dataset Information

The SPEI dataset (`spei01.nc`) is **362MB** and not included in the repository.

## Download Instructions

1. **Download SPEIbase v2.10** from:
   - Official source: https://spei.csic.es/database.html
   - Direct link: https://digital.csic.es/handle/10261/268088

2. **Select**: SPEI-01 (1-month scale)
3. **Format**: NetCDF
4. **Place** the downloaded `spei01.nc` file in this `data/` directory

## File Structure

```
data/
├── README.md                 # This file
├── continents.json           # Continental regions (included)
├── country_centroids.json    # Country coordinates (included)
└── spei01.nc                 # SPEI dataset (362MB - download separately)
```

## Alternative: Streamlit Cloud

When deploying to Streamlit Cloud, you can:
1. Upload the dataset directly via the Streamlit Cloud interface
2. Or use a cloud storage link (S3, Google Drive, etc.)

## Dataset Info

- **Size**: 362MB
- **Resolution**: 0.5° × 0.5°
- **Time Period**: January 1901 - December 2023
- **Variables**: SPEI (Standardized Precipitation Evapotranspiration Index)
