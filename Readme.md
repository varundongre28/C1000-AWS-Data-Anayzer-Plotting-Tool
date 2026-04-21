# IIG AWS Signal Analysis/Plotting Tool
**Developed by: Varun Dongre (Tech Officer), Indian Institute of Geomagnetism (IIG)**

## Overview
A specialized Python-based signal analysis tool for **Campbell Scientific Automatic Weather Stations (AWS)**. This tool is designed for R&D Officers and Engineers to process, filter, and visualize station data (TOA5 format) with high precision.

## Key Features
*   **Intelligent File Discovery:** Detects ASCII TOA5 files and warns users about Binary (.tob1) files.
*   **Signal Conditioning:** Built-in Moving Average Filters (3, 5, and 10-point) to remove high-frequency noise from environmental sensors.
*   **Scientific Visualization:** 
    *   Multi-panel plotting for Temperature, Wind, Solar Radiation, and Battery.
    *   Automated Peak/Trough detection with Red Up-Triangles ($\triangle$) and Blue Down-Triangles ($\nabla$).
    *   Smart X-Axis: Combines Time (HH:MM) and Date (DD-MMM) for high-resolution short-duration analysis.
*   **Professional Branding:** Standardized IIG header and gray boxed developer credits.

## Installation
Ensure you have Python installed, then run:
```bash
pip install pandas matplotlib numpy
