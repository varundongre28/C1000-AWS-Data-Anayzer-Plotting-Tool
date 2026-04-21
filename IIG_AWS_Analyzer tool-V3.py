import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator
import os
import sys
import warnings
import numpy as np

# Strict Command Window Size
try:
    myappid = 'IIG.AWS.DATA.ANALYSER TOOL.V3'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass


def set_console_size(cols=60, lines=35):
    """
    Uses ANSI Escape Sequences and Windows API to force a narrow width.
    """
    try:
        # 1. Try ANSI Escape Sequence (Works in modern Windows Terminal/PowerShell)
        sys.stdout.write(f"\x1b[8;{lines};{cols}t")
        sys.stdout.flush()

        # 2. Try classic Windows API (Works in CMD.exe)
        os.system(f'mode con: cols={cols} lines={lines}')
        
        # 3. Force Buffer size via Kernel32
        hOut = ctypes.windll.kernel32.GetStdHandle(-11)
        buf_size = ctypes.c_ulong(lines << 16 | cols)
        ctypes.windll.kernel32.SetConsoleScreenBufferSize(hOut, buf_size)
    except:
        pass
def set_plot_icon(fig):
    """Safely sets the window icon without causing memory/AttributeErrors."""
    try:
        logo_path = 'iig_logo.png'
        if not os.path.exists(logo_path):
            return
        backend = plt.get_backend()
        manager = plt.get_current_fig_manager()
        if 'TkAgg' in backend:
            from PIL import Image, ImageTk
            img = Image.open(logo_path)
            manager._icon = ImageTk.PhotoImage(img) 
            manager.window.iconphoto(False, manager._icon)
        elif 'Qt' in backend:
            from PyQt5 import QtGui
            manager.window.setWindowIcon(QtGui.QIcon(logo_path))
    except Exception:
        pass

def iig_header(folder="Not Selected", binary_found=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*60)
    print(" " * 10 + "INDIAN INSTITUTE OF GEOMAGNETISM (IIG)")
    print(" " * 13 + "CR1000 AWS DATA PLOTTING TOOL")
    print("="*60)
    print(f" Developer : Varun Dongre (Tech Officer) ")
    print(f" Last Update on - 20 April 2026 ")
    print("-" * 60)   
    print(f" [ DIRECTORY ] : {folder}")
    #print("-" * 120)
    if binary_found:
        print("-" * 60)
        print(" [!] CAUTION: BINARY DATA (.dat) DETECTED.")
        print(" [!] Use 'CardConvert' for TOA5 ASCII FILES.")
    print("-" * 60)

def main():
    set_console_size(60, 35)
    iig_header()
    working_dir = input("\n >> Enter Absolute Folder Path: ").strip().strip('"')
    if not os.path.isdir(working_dir): 
        print(" [!] Invalid Path. Exiting..."); sys.exit()
    os.chdir(working_dir)

    while True:
        # Check for binary files by extension
        bin_exists = any(f.lower().endswith('.tob1') for f in os.listdir('.'))
        iig_header(working_dir, bin_exists)
        
        # Recognize any .dat or .csv file
        files = [f for f in os.listdir('.') if f.lower().endswith(('.dat', '.csv'))]
        
        if not files:
            print(" [!] No data files found in this directory.")
            input(" Press Enter to change directory..."); main(); break

        print("\n [ INDEX ]   [ AVAILABLE AWS FILES ]")
        for i, f in enumerate(files):
            print(f"  {i:<10} {f}")
        print(f"  {'C':<10} Change Directory\n  {'Q':<10} Quit")
        
        cmd = input("\n >> Selection: ").strip().upper()
        if cmd == 'Q': sys.exit()
        if cmd == 'C': main(); break
        
        try:
            file_name = files[int(cmd)]
            
            # --- IMPROVED DATA TYPE RECOGNITION ---
            # Now recognizes renamed files by checking for keywords anywhere in the name
            fname_lower = file_name.lower()
            if "min" in fname_lower: dtype = "MINUTELY"
            elif "hour" in fname_lower: dtype = "HOURLY"
            elif "daily" in fname_lower: dtype = "DAILY"
            else: dtype = "STATION" # Default if name is custom (like AWSHourly2023...)

            # --- ROBUST BINARY ERROR CATCHING ---
            try:
                # Attempting to read TOA5 structure
                header_row = pd.read_csv(file_name, skiprows=1, nrows=1, encoding='utf-8').columns.tolist()
                df = pd.read_csv(file_name, skiprows=4, names=header_row, na_values=['NAN'], low_memory=False, encoding='utf-8')
            except (UnicodeDecodeError, pd.errors.ParserError):
                print("\n" + "!"*60)
                print(" [!] READ ERROR: UNABLE TO READ FILE CONTENT.")
                print(" [!] REASON: Selected file is in BINARY format.")
                print(" [!] ACTION: Use 'CardConvert'tool to convert binary into ASCII(TOA5)File.")
                print("!"*60)
                os.system('pause'); continue

            # Standardizing Timestamp
            df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'].astype(str).str.replace(' 24:00:00', ' 00:00:00'))
            df.set_index('TIMESTAMP', inplace=True)
            df.sort_index(inplace=True)
            
        except Exception as e:
            print(f" [!] Error during file load: {e}"); os.system('pause'); continue

        # Filtering Selection
        print("    [MOVING AVERAGE FILTERING ]    ")
        print("[0] Raw [1] 3-pt [2] 5-pt [3] 10-pt")
        f_in = input(" >> Select Filter Strength: ").strip()
        window = {"1": 3, "2": 5, "3": 10}.get(f_in, 1)
        filter_text = f" ({window}-pt Moving Avg)" if window > 1 else " (Raw Signal)"

        if window > 1:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].rolling(window=window, center=True).mean()

        min_d, max_d = df.index.min(), df.index.max()
        print(f"\n     [ DATA AVAILABLE FROM ]    ")
        print(f"{min_d} to {max_d}")
        s_input = input(f" >> Plot Start (YYYY-MM-DD): ") or str(min_d.date())
        e_input = input(f" >> Plot End   (YYYY-MM-DD): ") or str(max_d.date())

        try:
            plot_df = df[s_input:e_input]
            if plot_df.empty:
                print(" [!] Selected date range contains no data."); os.system('pause'); continue

            # Parameter Mapping
            groups = {
                "Temperature (°C)": [c for c in plot_df.columns if "AirTC" in c and "Avg" in c],
                "Wind Speed (m/s)": [c for c in plot_df.columns if "WS_ms" in c and "Avg" in c],
                "Wind Direction (°)": [c for c in plot_df.columns if "WindDir" in c],
                "Solar Rad (W/m²)": [c for c in plot_df.columns if "Slr" in c and "Avg" in c],
                "Battery (V)": [c for c in plot_df.columns if "Batt" in c and "Min" in c]
            }
            groups = {k: v for k, v in groups.items() if v}

            fig = plt.figure(num=f"AWS_{dtype}_{s_input}_to_{e_input}", figsize=(16, 11))
            axes = fig.subplots(len(groups), 1, sharex=True)
            colors = ['#1f77b4', '#d62728', '#2ca02c', '#9467bd', '#ff7f0e']

            for i, (title, cols) in enumerate(groups.items()):
                ax = axes[i]
                col = cols[0]
                series = plot_df[col].dropna()
                if series.empty: continue
                
                v_min, v_max, v_avg = series.min(), series.max(), series.mean()
                t_min, t_max = series.idxmin(), series.idxmax()
                
                ax.plot(series.index, series, color=colors[i%len(colors)], linewidth=1.0)
                ax.scatter(t_max, v_max, color='red', marker='^', s=45, zorder=6)
                ax.scatter(t_min, v_min, color='blue', marker='v', s=45, zorder=6)

                # Custom Title Position as requested
                ax.text(0.008, 0.96, title.upper(), transform=ax.transAxes, 
                        fontsize=8, fontweight='bold', va='top', ha='left')
                
                ax.grid(True, which='major', linestyle=':', alpha=0.6, color='gray')
                ax.grid(True, which='minor', linestyle=':', alpha=0.3, color='lightgray')
                ax.xaxis.set_minor_locator(AutoMinorLocator())
                ax.yaxis.set_minor_locator(AutoMinorLocator())
                
                # Legend Stacking and Color Coding
                ax.plot([], [], ' ', label=f"{col} | Avg: {v_avg:.2f}")
                ax.plot([], [], marker='^', color='red', linestyle='None', label=f"Max: {v_max:.2f}")
                ax.plot([], [], marker='v', color='blue', linestyle='None', label=f"Min: {v_min:.2f}")
                ax.legend(loc='upper right', fontsize=7, ncol=1, framealpha=0.5).set_draggable(True)
                
                if "Direction" in title: ax.set_ylim(-20, 380)

            # Branding Box - Aligned to Subplot 1
            axes[0].text(1.0, 1.05, 'Developed by: Varun Dongre (Tech Officer), IIG', 
                         transform=axes[0].transAxes, ha='right', fontsize=6, fontweight='bold', 
                         color='gray', bbox=dict(facecolor='none', edgecolor='lightgray', boxstyle='round,pad=0.2'))

            # Smart X-Axis Formatting
            delta = plot_df.index.max() - plot_df.index.min()
            if delta.days <= 2:
                axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d-%b'))
            else:
                axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            
            plt.suptitle(f"INDIAN INSTITUTE OF GEOMAGNETISM\nAWS {dtype} DATA PLOTS{filter_text} | PERIOD: {s_input} to {e_input}", 
                         fontsize=12, fontweight='bold', color='#003366', y=0.97)
            
            fig.text(0.98, 0.01, f"Year: {plot_df.index[0].year}", ha='right', fontsize=10, fontweight='bold')

            plt.tight_layout(rect=[0, 0.03, 1, 0.93])
            
            # Save using the recognized Data Type
            save_fn = f"AWS_{dtype}_{s_input}_to_{e_input}.png"
            plt.savefig(save_fn, dpi=300)
            print(f"\n [SUCCESS] Plot saved as: {save_fn}")
            plt.show()
            
        except Exception as e:
            print(f" [!] Visualization Error: {e}"); os.system('pause')

if __name__ == "__main__":
    main()
