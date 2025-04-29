import tkinter as tk
from gui12 import FootballAnalyzerGUI

def main():
    root = tk.Tk()
    app = FootballAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()