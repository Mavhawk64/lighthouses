# 🏮 Lighthouses of the United States

A data visualization project to fetch, store, and beautifully map all lighthouses across the United States. This project aims to create a stunning dark-themed map displaying lighthouse locations as bright beacons, inspired by the elegant visualizations seen on r/dataisbeautiful.

## 📖 Project Overview

This repository implements a complete pipeline to:

1. **Data Collection**: Scrape lighthouse names from the US Coast Guard historical database
2. **Geolocation**: Automatically obtain latitude/longitude coordinates for each lighthouse
3. **Visualization**: Create a beautiful dark map of the USA with lighthouses displayed as bright white or yellow points

### 🎯 Inspiration

This project is inspired by beautiful lighthouse visualizations like [this one](https://www.reddit.com/r/dataisbeautiful/comments/1motron/lighthouses_of_the_united_states_oc/) from r/dataisbeautiful, which showcases the poetic beauty of lighthouse data when properly visualized.

## 🗂️ Project Structure

```
lighthouses/
├── README.md              # This file
├── data/                  # Data storage directory
│   ├── raw/              # Raw scraped data
│   ├── processed/        # Cleaned and processed data
│   └── lighthouse_data.json  # Final lighthouse dataset
├── src/                   # Source code
│   ├── scraper/          # Web scraping modules
│   ├── geocoder/         # Geolocation utilities
│   └── visualizer/       # Map generation code
├── maps/                  # Generated visualizations
├── requirements.txt       # Python dependencies
└── config.yaml           # Configuration settings
```

## 🌊 Data Source

**Primary Source**: [US Coast Guard Historical Lighthouse Database](https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Lighthouses/)

The US Coast Guard maintains a comprehensive historical database of lighthouses, which serves as our authoritative source for lighthouse names and locations across the United States.

## 🚀 Implementation Phases

### Phase 1: Data Collection 📊
- **Objective**: Scrape lighthouse names from the Coast Guard website
- **Output**: Raw list of lighthouse names stored in `data/raw/lighthouse_names.txt`
- **Tools**: Python with BeautifulSoup, requests, or Scrapy
- **Challenges**: Handle pagination, rate limiting, and data cleaning

### Phase 2: Geolocation 🗺️
- **Objective**: Obtain precise latitude/longitude coordinates for each lighthouse
- **Methods**: 
  - Google Maps Geocoding API
  - OpenStreetMap Nominatim API
  - USGS Geographic Names Information System (GNIS)
- **Output**: Complete dataset in `data/lighthouse_data.json`
- **Data Format**:
  ```json
  {
    "lighthouses": [
      {
        "name": "Boston Light",
        "state": "Massachusetts",
        "latitude": 42.3275,
        "longitude": -70.8908,
        "year_built": 1716,
        "status": "active"
      }
    ]
  }
  ```

### Phase 3: Visualization 🎨
- **Objective**: Create a stunning map visualization
- **Style Requirements**:
  - **Background**: Dark color scheme (navy blue, black, or dark gray)
  - **Lighthouse Markers**: Bright white or yellow points
  - **Map Style**: Clean, minimal US outline
  - **Optional**: Glow effects around lighthouse points
- **Tools**: 
  - Python: Matplotlib, Plotly, or Folium
  - JavaScript: D3.js or Leaflet
  - R: ggplot2 with custom themes

## 🛠️ Technical Requirements

### Dependencies
- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`):
  - `requests` - HTTP library for web scraping
  - `beautifulsoup4` - HTML parsing
  - `pandas` - Data manipulation
  - `geopandas` - Geographic data handling
  - `matplotlib` - Static plotting
  - `plotly` - Interactive visualizations
  - `folium` - Web mapping
  - `geocoder` - Geocoding services

### Environment Setup
```bash
# Clone the repository
git clone https://github.com/Mavhawk64/lighthouses.git
cd lighthouses

# Create virtual environment
python -m venv lighthouse_env
source lighthouse_env/bin/activate  # On Windows: lighthouse_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/{raw,processed} maps
```

## 📋 Usage Instructions

### 1. Data Collection
```bash
# Run the lighthouse name scraper
python src/scraper/coast_guard_scraper.py

# Verify collected data
head data/raw/lighthouse_names.txt
```

### 2. Geolocation
```bash
# Geocode lighthouse locations
python src/geocoder/lighthouse_geocoder.py

# Check processing results
python -c "import json; print(len(json.load(open('data/lighthouse_data.json'))['lighthouses']))"
```

### 3. Visualization
```bash
# Generate the lighthouse map
python src/visualizer/create_lighthouse_map.py

# Output will be saved to maps/lighthouse_map.html or maps/lighthouse_map.png
```

## 🎨 Visualization Features

### Map Styling
- **Color Palette**: 
  - Background: `#0f1419` (dark navy)
  - Water: `#1a1a2e` (darker blue)
  - Land: `#16213e` (muted blue-gray)
  - Lighthouses: `#ffd700` (golden yellow) or `#ffffff` (pure white)

### Interactive Elements
- Hover tooltips showing lighthouse name, location, and year built
- Zoom and pan capabilities
- Optional clustering for dense regions
- Filter options by state, construction period, or operational status

## 📊 Expected Output

The final visualization will be a high-quality map showing:
- ~1,000+ lighthouse locations across the US coastlines and Great Lakes
- Beautiful contrast between dark map and bright lighthouse points
- Clean, publication-ready aesthetics suitable for r/dataisbeautiful
- Both static (PNG/SVG) and interactive (HTML) versions

## 🔮 Future Enhancements

- [ ] **Historical Timeline**: Animate lighthouse construction over time
- [ ] **Lighthouse Details**: Add height, range, and architectural style data
- [ ] **3D Visualization**: Create elevation-aware 3D maps
- [ ] **Mobile App**: Develop a lighthouse finder mobile application
- [ ] **API Integration**: Real-time operational status from Coast Guard
- [ ] **International Expansion**: Include lighthouses from other countries

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests for:
- Additional data sources
- Improved geocoding accuracy
- Enhanced visualization styles
- Performance optimizations
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **US Coast Guard** for maintaining the historical lighthouse database
- **r/dataisbeautiful community** for inspiration and feedback
- **OpenStreetMap contributors** for geographic data
- **Lighthouse preservation societies** for historical information

---

*"A lighthouse is not interested in who gets its light! It just gives it without thinking! Giving light is its nature!"* - Mehmet Murat Ildan