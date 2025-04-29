import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import os

class FootballPerformanceAnalyzer:
    def __init__(self):
        self.player_detector = YOLO('yolov8n.pt')
        self.player_tracks = defaultdict(list)
        self.player_speeds = defaultdict(list)
        self.player_distances = defaultdict(float)
        self.player_images = {}  # Stores cropped player images
        self.frame_count = 0
        self.fps = 30
        self.current_frame = None
        self.pixel_to_meter = 0.1
        self.frame_width = 1280
        self.frame_height = 720
        self.player_stats = {}

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._reset_tracking()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            self.current_frame = frame.copy()
            results = self.player_detector.track(frame, persist=True, classes=[0])
            self._update_player_positions(results, frame)
            self.frame_count += 1

        cap.release()
        self._calculate_player_statistics()
        return self.player_stats, self.player_images

    def _reset_tracking(self):
        self.player_tracks = defaultdict(list)
        self.player_speeds = defaultdict(list)
        self.player_distances = defaultdict(float)
        self.player_images = {}
        self.frame_count = 0

    def _update_player_positions(self, results, frame):
        if results[0].boxes.id is None:
            return

        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().numpy()

        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # Store cropped player image (only once per player)
            if track_id not in self.player_images:
                cropped = frame[int(y1):int(y2), int(x1):int(x2)]
                if cropped.size > 0:
                    self.player_images[track_id] = cropped

            # Update tracking data
            if self.player_tracks[track_id]:
                prev_x, prev_y = self.player_tracks[track_id][-1]
                distance = np.sqrt((center_x-prev_x)**2 + (center_y-prev_y)**2)
                self.player_distances[track_id] += distance * self.pixel_to_meter
                speed = (distance * self.pixel_to_meter * self.fps) * 3.6  # km/h
                self.player_speeds[track_id].append(speed)

            self.player_tracks[track_id].append((center_x, center_y))

    def _calculate_player_statistics(self):
        self.player_stats = {}
        for player_id in self.player_tracks:
            if len(self.player_tracks[player_id]) < 2:
                continue

            positions = np.array(self.player_tracks[player_id])
            speeds = self.player_speeds[player_id]

            self.player_stats[player_id] = {
                'distance': float(self.player_distances[player_id]),
                'avg_speed': float(np.mean(speeds)) if speeds else 0,
                'max_speed': float(np.max(speeds)) if speeds else 0,
                'positions': positions.tolist()
            }

    def generate_player_card(self, player_id):
        if player_id not in self.player_stats:
            return None

        stats = self.player_stats[player_id]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis('off')
        
        # Add player image if available
        if player_id in self.player_images:
            player_img = cv2.cvtColor(self.player_images[player_id], cv2.COLOR_BGR2RGB)
            ax.imshow(player_img)
            ax.set_title(f"Player {player_id}", pad=20)
        
        # Add stats text
        stats_text = (
            f"Distance: {stats['distance']:.2f}m\n"
            f"Avg Speed: {stats['avg_speed']:.2f}km/h\n"
            f"Max Speed: {stats['max_speed']:.2f}km/h"
        )
        ax.text(0.5, -0.1, stats_text, transform=ax.transAxes, 
               ha='center', va='top', fontsize=10)
        
        plt.tight_layout()
        return fig

    def generate_heatmap(self, player_id):
        if player_id not in self.player_stats:
            return None

        positions = np.array(self.player_stats[player_id]['positions'])
        fig, ax = plt.subplots(figsize=(6, 4))
        
        if len(positions) > 1:
            sns.kdeplot(x=positions[:,0], y=positions[:,1], 
                       cmap='hot', fill=True, ax=ax)
            ax.set_title(f"Player {player_id} Heatmap")
        else:
            ax.scatter(positions[:,0], positions[:,1], c='red', s=50)
            
        ax.set_xlim(0, self.frame_width)
        ax.set_ylim(self.frame_height, 0)
        plt.tight_layout()
        return fig
