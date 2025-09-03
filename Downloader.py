#!/usr/bin/env python3
"""
yt-dlp playlist GUI
- Numbering: 1, 2, 3 ... (no zero-padding)
- No thumbnails (video+audio only) -> merged to MP4
- Improved UI: ttk, grid, resizable window, progress, status, Stop button
- Thread-safe logging via .after(...)
"""
import subprocess, threading, signal
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk

CONCURRENT = 8
# Unpadded numbering: 1, 2, 3...
TEMPLATE = "%(playlist_title)s/%(playlist_index)d - %(title)s.%(ext)s"

def build_cmd(url: str, out_dir: Path, cookies: str | None, archive_file: Path):
    cmd = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "--concurrent-fragments", str(CONCURRENT),
        "--ignore-errors",
        "--embed-metadata",
        "--download-archive", str(archive_file),
        "-o", TEMPLATE,
        "--paths", str(out_dir),
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    cmd.append(url)
    return cmd

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("yt-dlp Playlist Downloader")
        self.geometry("820x560")
        # Enable minimize/maximize and resizing
        self.resizable(True, True)

        # Optional: pick a nicer ttk theme if available
        try:
            style = ttk.Style(self)
            for theme in ("vista", "clam", "default"):
                if theme in style.theme_names():
                    style.theme_use(theme)
                    break
        except Exception:
            pass

        # Root container and responsive layout
        root = ttk.Frame(self, padding=10)
        root.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)  # center column stretches
        root.columnconfigure(2, weight=0)
        # let the log row expand
        root.rowconfigure(7, weight=1)

        # URL
        ttk.Label(root, text="Playlist URL:").grid(row=0, column=0, sticky="w")
        self.url = tk.StringVar()
        ttk.Entry(root, textvariable=self.url, width=95).grid(row=1, column=0, columnspan=3, sticky="we", pady=(4, 8))

        # Destination folder
        ttk.Label(root, text="Download folder:").grid(row=2, column=0, sticky="w")
        self.dst = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(root, textvariable=self.dst, width=75).grid(row=2, column=1, sticky="we", padx=(6, 6))
        ttk.Button(root, text="Browse…", command=self.pick_dir).grid(row=2, column=2, sticky="we")

        # Cookies (optional)
        ttk.Label(root, text="Cookies file (optional):").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.ck = tk.StringVar()
        ttk.Entry(root, textvariable=self.ck, width=75).grid(row=3, column=1, sticky="we", padx=(6, 6), pady=(8, 0))
        ttk.Button(root, text="Browse…", command=self.pick_cookie).grid(row=3, column=2, sticky="we", pady=(8, 0))

        # Controls
        self.start_btn = ttk.Button(root, text="Start download", command=self.start)
        self.start_btn.grid(row=4, column=0, pady=10, sticky="w")

        self.stop_btn = ttk.Button(root, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=4, column=1, pady=10, sticky="w")

        self.status = tk.StringVar(value="Idle")
        ttk.Label(root, textvariable=self.status).grid(row=4, column=2, sticky="e")

        # Progress bar
        self.pbar = ttk.Progressbar(root, mode="indeterminate", length=260)
        self.pbar.grid(row=5, column=0, columnspan=3, sticky="we", pady=(0, 8))

        # Separator
        ttk.Separator(root, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="we", pady=(0, 6))

        # Log
        ttk.Label(root, text="Log:").grid(row=6, column=0, sticky="w", pady=(0, 2))
        self.log = scrolledtext.ScrolledText(root, width=110, height=18, state="disabled")
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew")

        # Internal state
        self._worker = None
        self._proc: subprocess.Popen | None = None

    # Helpers
    def pick_dir(self):
        d = filedialog.askdirectory(initialdir=self.dst.get())
        if d:
            self.dst.set(d)

    def pick_cookie(self):
        f = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if f:
            self.ck.set(f)

    def log_write(self, txt: str):
        self.log["state"] = "normal"
        self.log.insert(tk.END, txt + "\n")
        self.log.see(tk.END)
        self.log["state"] = "disabled"

    def _log_main(self, txt: str):
        # Called on main thread via .after(...)
        self.log_write(txt)

    def run_dl(self, cmd):
        self.after(0, self._log_main, "Running: " + " ".join(cmd))
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            assert self._proc.stdout is not None
            for line in self._proc.stdout:
                self.after(0, self._log_main, line.rstrip())
            self._proc.wait()
            code = self._proc.returncode
            self.after(0, self._log_main, "✔ Done" if code == 0 else f"yt-dlp exited {code}")
        except Exception as e:
            self.after(0, self._log_main, f"Error: {e}")
        finally:
            self._proc = None
            self.after(0, self._on_finish)

    def _on_finish(self):
        self.pbar.stop()
        self.status.set("Idle")
        self.start_btn["state"] = "normal"
        self.stop_btn["state"] = "disabled"

    def start(self):
        u = self.url.get().strip()
        if not u:
            messagebox.showerror("Missing URL", "Enter a playlist URL")
            return

        d = Path(self.dst.get()).expanduser()
        d.mkdir(parents=True, exist_ok=True)

        # Archive file at destination root (no template expansion)
        archive_file = d / "archive.txt"
        c = self.ck.get().strip() or None

        cmd = build_cmd(u, d, c, archive_file)

        self.status.set("Working…")
        self.start_btn["state"] = "disabled"
        self.stop_btn["state"] = "normal"
        self.pbar.start(12)

        self._worker = threading.Thread(target=self.run_dl, args=(cmd,), daemon=True)
        self._worker.start()

    def stop(self):
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                try:
                    self._proc.send_signal(signal.SIGINT)
                except Exception:
                    pass
        self.status.set("Stopping…")

if __name__ == "__main__":
    App().mainloop()
