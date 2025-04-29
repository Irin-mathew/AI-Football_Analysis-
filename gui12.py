import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import os
import threading
from football_analyzer import FootballPerformanceAnalyzer  # Import our analyzer class

class FootballAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Performance Analyzer")
        self.root.geometry("1200x800")
        
        # Initialize the analyzer
        self.analyzer = FootballPerformanceAnalyzer()
        
        # Variables
        self.video_path = None
        self.current_frame = None
        self.is_processing = False
        self.selected_player_id = None
        self.cropped_players = []  # List of cropped player images
        
        # Create GUI elements
        self._create_menu()
        self._create_main_frame()
        
    def _create_menu(self):
        """Create the application menu"""
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Video", command=self._open_video)
        file_menu.add_command(label="Process Video", command=self._process_video)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)
    
    def _create_main_frame(self):
        """Create the main application frame"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Video and controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Video display
        self.video_frame = ttk.LabelFrame(left_panel, text="Video Display")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.video_canvas = tk.Canvas(self.video_frame, bg="black")
        self.video_canvas.pack(fill=tk.BOTH, expand=True)
        self.video_canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Video controls
        controls_frame = ttk.Frame(left_panel)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Load Video", command=self._open_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Process", command=self._process_video).pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(controls_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Right panel - Player selection and stats
        right_panel = ttk.Frame(main_frame, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Player selection
        player_frame = ttk.LabelFrame(right_panel, text="Player Selection")
        player_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.player_listbox = tk.Listbox(player_frame, height=5)
        self.player_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.player_listbox.bind("<<ListboxSelect>>", self._on_player_select)
        
        # Cropped players frame
        self.cropped_frame = ttk.LabelFrame(right_panel, text="Detected Players")
        self.cropped_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cropped_canvas = tk.Canvas(self.cropped_frame, height=100)
        self.cropped_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        # Stats display
        stats_frame = ttk.LabelFrame(right_panel, text="Player Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabs for different visualizations
        tab_control = ttk.Notebook(stats_frame)
        
        self.stats_tab = ttk.Frame(tab_control)
        self.heatmap_tab = ttk.Frame(tab_control)
        
        tab_control.add(self.stats_tab, text='Player Card')
        tab_control.add(self.heatmap_tab, text='Heatmap')
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Stats content
        self.stats_content = ttk.Frame(self.stats_tab)
        self.stats_content.pack(fill=tk.BOTH, expand=True)
        
        # Heatmap content
        self.heatmap_content = ttk.Frame(self.heatmap_tab)
        self.heatmap_content.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Load a video to begin.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _open_video(self):
        """Open a video file"""
        self.video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        
        if self.video_path:
            # Display first frame
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            if ret:
                self._display_frame(frame)
                self.status_var.set(f"Loaded video: {os.path.basename(self.video_path)}")
            cap.release()
    
    def _display_frame(self, frame):
        """Display a frame on the video canvas"""
        self.current_frame = frame.copy()
        
        # Resize the frame to fit the canvas
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate aspect ratio-preserving dimensions
            frame_height, frame_width = frame.shape[:2]
            ratio = min(canvas_width/frame_width, canvas_height/frame_height)
            new_width = int(frame_width * ratio)
            new_height = int(frame_height * ratio)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB for display
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(rgb_frame)
            self.photo = ImageTk.PhotoImage(image=img)
            
            # Update canvas
            self.video_canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo, anchor=tk.CENTER)
    
    def _process_video(self):
        """Process the video in a separate thread"""
        if not self.video_path or self.is_processing:
            return
            
        self.is_processing = True
        self.status_var.set("Processing video... This may take a while.")
        self.progress_var.set(0)
        
        # Start processing thread
        thread = threading.Thread(target=self._run_processing)
        thread.daemon = True
        thread.start()
    
    def _run_processing(self):
        """Run the video processing"""
        try:
            # Process the video
            self.analyzer.process_video(self.video_path)
            
            # Update player list
            self.root.after(0, self._update_player_list)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("Processing complete. Select a player to view statistics."))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.progress_var.set(100))
    
    def _update_player_list(self):
        """Update the player list with detected players"""
        self.player_listbox.delete(0, tk.END)
        
        for player_id in self.analyzer.player_stats:
            self.player_listbox.insert(tk.END, f"Player {player_id}")
            
            # For demo purposes, create cropped player images
            # In a real application, these would come from the video frames
            self._add_cropped_player(player_id)
    
    def _add_cropped_player(self, player_id):
        """Add a cropped player image to the selection area"""
        # In a real app, this would use actual cropped images
        # For this demo, we'll create colored rectangles
        
        # Create a small colored image
        color = np.random.randint(0, 255, 3)
        img = np.ones((50, 40, 3), dtype=np.uint8)
        img[:, :] = color
        
        # Add player ID text
        cv2.putText(img, f"P{player_id}", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Convert to PhotoImage
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        photo = ImageTk.PhotoImage(image=pil_img)
        
        # Keep reference to avoid garbage collection
        self.cropped_players.append(photo)
        
        # Add to canvas
        x_pos = len(self.cropped_players) * 50
        img_id = self.cropped_canvas.create_image(x_pos, 50, image=photo)
        
        # Bind click event
        self.cropped_canvas.tag_bind(img_id, "<Button-1>", lambda event, pid=player_id: self._select_player(pid))
    
    def _on_canvas_click(self, event):
     """Handle click on the video canvas"""
     if not hasattr(self, 'current_frame') or self.current_frame is None:
        return
        
     x, y = event.x, event.y
     self.status_var.set(f"Clicked at ({x}, {y})")
    
    def _on_player_select(self, event):
        """Handle selection from the player listbox"""
        if not self.player_listbox.curselection():
            return
            
        index = self.player_listbox.curselection()[0]
        player_text = self.player_listbox.get(index)
        
        # Extract player ID from text
        player_id = int(player_text.split()[1])
        self._select_player(player_id)
    
    def _select_player(self, player_id):
        """Select a player and display their statistics"""
        self.selected_player_id = player_id
        
        # Update status
        self.status_var.set(f"Selected Player {player_id}")
        
        # Display player card
        self._display_player_card(player_id)
        
        # Display heatmap
        self._display_heatmap(player_id)
    
    def _display_player_card(self, player_id):
        """Display the player card for the selected player"""
        # Clear previous content
        for widget in self.stats_content.winfo_children():
            widget.destroy()
            
        if player_id not in self.analyzer.player_stats:
            return
            
        # Generate player card
        fig = self.analyzer.generate_player_card(player_id)
        
        if fig:
            # Embed the figure in the Tkinter frame
            canvas = FigureCanvasTkAgg(fig, master=self.stats_content)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _display_heatmap(self, player_id):
        """Display the heatmap for the selected player"""
        # Clear previous content
        for widget in self.heatmap_content.winfo_children():
            widget.destroy()
            
        if player_id not in self.analyzer.player_stats:
            return
            
        # Generate heatmap
        fig = self.analyzer.generate_heatmap(player_id)
        
        if fig:
            # Embed the figure in the Tkinter frame
            canvas = FigureCanvasTkAgg(fig, master=self.heatmap_content)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = FootballAnalyzerGUI(root)
    root.mainloop()