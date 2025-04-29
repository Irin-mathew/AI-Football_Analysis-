# Football Performance Analyzer

A computer vision-based tool for tracking and analyzing football player performance from video footage.

## Overview

This application uses the YOLOv8 object detection model to track football players in video footage and generate performance statistics. The tool provides insights into player movement patterns, distances covered, speeds, and position heat maps.

## Features

- **Player Detection and Tracking**: Automatically detects and tracks player movement throughout video footage
- **Performance Metrics**: Calculates key performance statistics like:
  - Distance covered
  - Average speed
  - Maximum speed
  - Movement patterns
- **Visual Analytics**: 
  - Player position heat maps
  - Player performance cards
  - Interactive player selection interface

## Requirements

- Python 3.8+
- OpenCV
- NumPy
- Ultralytics YOLOv8
- Matplotlib
- Seaborn
- tkinter
- PIL (Pillow)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/football-performance-analyzer.git
   cd football-performance-analyzer
   ```

2. Install dependencies:
   ```
   pip install opencv-python numpy ultralytics matplotlib seaborn pillow
   ```

3. Install YOLOv8:
   ```
   pip install ultralytics
   ```

## Usage

1. Run the main.py file:
   ```
   python main.py
   ```

2. Use the interface to:
   - Load a football video file
   - Process the video for player tracking
   - Select players to view their performance statistics
   - View heat maps of player movements

## Project Structure

- `football_analyser.py`: Core analysis engine that processes video and generates statistics
- `gui12.py`: Tkinter-based GUI implementation
- `main.py`: Application entry point

## How It Works

1. The application uses YOLOv8 to detect players in each video frame
2. It tracks player positions across frames
3. Calculates distance, speed, and other metrics based on position changes
4. Generates visualizations and statistics for each detected player

## Output Visualizations

The Football Performance Analyzer provides powerful visual insights into player performance through intuitive visualizations.

### Player Statistics & Selection Interface
(Output1.png)
The player selection interface allows coaches and analysts to:
- Select individual players from the detected roster
- View high-resolution cropped images of each player for easy identification
- Access comprehensive performance metrics for the selected player including:
  - Total distance covered during the match
  - Average movement speed
  - Maximum sprint speed 
  - Time-based performance trends

This intuitive interface bridges the gap between raw data and actionable insights, making it easy to compare player performances and make informed decisions during training and match preparation.

### Player Movement Heatmaps

(Output2.png)
The heatmap visualization provides a spatial analysis of player movement patterns:
- Color intensity represents time spent in different areas of the pitch
- Identifies player positioning tendencies and zone preferences
- Highlights defensive coverage and attacking movement patterns
- Shows participation in different phases of play

Coaches can use these heatmaps to analyze positioning discipline, identify spatial weaknesses in formation, and recognize player movement patterns that might not be apparent from traditional statistics alone.

These visual analytics transform complex tracking data into clear, actionable insights that can inform tactical decisions and player development strategies.

## Acknowledgments

- This project uses the YOLOv8 model from Ultralytics
