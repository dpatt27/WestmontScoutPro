# WestmontScoutPro

## Overview

Westmont Scout Pro is a web-based application designed to help the Westmont Baseball Team analyze TrackMan-generated CSV data. It enables staff and student managers to upload files, process data, and generate heatmaps and postgame reports. The app streamlines data analysis, making key insights more accessible and actionable.

### Features

- CSV File Upload: Users can upload raw TrackMan CSV files.

- Data Storage: Processed data is stored in a SQL database.

- Heatmaps & Reports: Generate heatmaps of pitch locations and postgame analytics.

- Filtering: Users can filter results by pitch type, player, or outcome.

- Fast Processing: Heatmaps generated in under 10 seconds.

### Technologies Used

- Frontend: Django (Python-based web framework)

- Backend: Python/Django for data processing

- Database: SQL for storing TrackMan data

- Visualization: Matplotlib/Plotly for heatmaps and analytics reports

### Usage

1. Upload Data: Navigate to the upload page and select a TrackMan CSV file.

2. Process Data: The system cleans and stores data in the SQL database.

3. Generate Heatmaps: Select filters to visualize pitch tendencies and hot zones.

4. Download Reports: Export postgame analytics as a PDF or CSV.

### License

This project is licensed under the MIT License.