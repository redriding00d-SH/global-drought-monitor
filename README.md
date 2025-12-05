# 🌍 Global Drought Monitoring Dashboard

An interactive web application for visualizing and analyzing global drought patterns using SPEI (Standardized Precipitation Evapotranspiration Index) data.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features

- 📊 **Interactive Global Map** - Visualize drought patterns worldwide
- 🌍 **Continental Views** - Detailed analysis for 6 continents
- 🗺️ **Mapbox Integration** - Professional map visualizations
- 📅 **Historical Data** - Access data from 1901 to 2023
- 🎯 **State/Country Level** - Granular drought severity categorization
- 📈 **Real-time Statistics** - Mean, median, std dev, min/max SPEI values

## 🚀 Live Demo

Current Live Demo [Streamlit Webapp](https://global-drought-monitor-zzbxx5dpjzbqsxzxxkbao7.streamlit.app/) 
[Deploy to Streamlit Cloud](https://streamlit.io/cloud) 

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- Mapbox API token (free tier available)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/redriding00d-SH/global-drought-monitor.git
   ```
   ```bash
   git lfs install  # Required for downloading the 362MB dataset
   ``` 

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the dataset** (362MB - not included in repo)
   - Visit: https://spei.csic.es/database.html
   - Download SPEI-01 (1-month scale) in NetCDF format
   - Place `spei01.nc` in the `data/` directory
   - See `data/README.md` for details

4. **Set up secrets**
   ```bash
   mkdir -p .streamlit
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   Edit `.streamlit/secrets.toml` and add your Mapbox token:
   ```toml
   MAPBOX_TOKEN = "your_actual_mapbox_token_here"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   ```
   Navigate to http://localhost:8501
   ```

## 🌐 Deploy to Streamlit Cloud

1. **Push to GitHub** (secrets are automatically excluded via `.gitignore`)
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Choose `app.py` as the main file

3. **Add secrets in Streamlit Cloud**
   - Go to App Settings → Secrets
   - Add your Mapbox token:
     ```toml
     MAPBOX_TOKEN = "your_mapbox_token_here"
     ```

4. **Deploy!** 🎉

## 📁 Project Structure

```
drought-ai-project/
├── app.py                          # Main Streamlit application
├── utils.py                        # Utility functions
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── data/
│   ├── spei01.nc                   # SPEI dataset (NetCDF)
│   ├── continents.json             # Continental regions & countries
│   └── country_centroids.json      # Country coordinates
├── .streamlit/
│   ├── secrets.toml.example        # Example secrets file
│   └── secrets.toml                # Your actual secrets (gitignored)
└── assets/
    └── fonts/
        └── Geist-VariableFont_wght.ttf
```

## 🔑 Get a Mapbox Token

1. Go to [mapbox.com](https://www.mapbox.com/)
2. Sign up for a free account
3. Navigate to Account → Access Tokens
4. Create a new token or copy the default public token
5. Free tier includes **50,000 free map loads/month** ✅

## 📊 Data Source

**SPEIbase v2.10**
- Source: CRU TS 4.08
- Time Period: January 1901 - December 2023
- Resolution: 0.5° × 0.5° global grid
- Citation: Vicente-Serrano et al. (2010)

## 🗺️ Covered Regions

- 🌍 Africa (54 countries)
- 🌎 North America (23 countries)
- 🌏 Asia (48 countries)
- 🇪🇺 Europe (47 countries)
- 🌎 South America (12 countries)
- 🌏 Australia (8 states + New Zealand)

## 💡 Usage Examples

### View Global Drought Patterns
1. Select "Global" from the region dropdown
2. Choose a date using the Month/Year selectors
3. Explore the interactive map

### Analyze a Specific Continent
1. Click on the continent tab (e.g., "Africa")
2. View drought severity by country
3. Check regional statistics

### Compare Time Periods
1. Change the date using sidebar controls
2. Observe how drought patterns evolve over time

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SPEI data: Global SPEI database
- Maps: Mapbox
- Framework: Streamlit
- Font: Geist by Vercel

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit**
