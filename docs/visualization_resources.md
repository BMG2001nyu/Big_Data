# Visualization Resources

## Tableau Workbook Setup
1. Download processed parquet outputs (`data/processed/` or `data/processed_dask/`).
2. In Tableau, choose **Connect > To a File > Parquet** and point to the processed directory.
3. Create extracted data source with the following recommended fields:
   - Dimensions: `date`, `hour`, `borough`, `roadwayname`, `is_peak_hour`, `is_weekend`
   - Measures: `vehicle_count`, `volume_per_minute`, `congestion_index`, `weekpart_congestion_ratio`
4. Suggested visualizations:
   - Heatmap of `hour` vs `date` with `vehicle_count` color intensity.
   - Bar chart comparing weekday vs weekend congestion by borough.
   - Dashboard combining peak-hour highlights, anomaly counts, and congestion trends.

## Python Visualization Stack
- **Matplotlib/Seaborn** for statistical summaries in notebooks.
- **Plotly** for interactive trend analysis shared with stakeholders.
- Reference notebooks `notebooks/01_data_overview.ipynb` and `notebooks/02_feature_analysis.ipynb` for sample plots.

## Dashboard Integration
- The React dashboard (`dashboard/`) consumes `/api/traffic/*` endpoints for operational KPIs.
- Supplement Plotly exports by saving figures as HTML and embedding them in knowledge bases or presentations.

