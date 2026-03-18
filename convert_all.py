import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from moviepy import AudioFileClip
import threading

class VideoToMp3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("Video to MP3 Converter")
        self.root.geometry("600x550")
        
        self.supported_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.mpg', '.mpeg')
        
        self.input_files = []
        self.output_folder = tk.StringVar(value="")
        
        # Initialize UI elements to avoid linting errors
        self.file_count_label = None
        self.start_btn = None
        self.log_area = None
        self.progress_bar = None
        self.browse_files_btn = None
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. เลือกไฟล์วิดีโอก่อน (Input Files)
        tk.Label(main_frame, text="1. เลือกไฟล์วิดีโอ (Input Files):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        file_btn_frame = tk.Frame(main_frame)
        file_btn_frame.pack(fill=tk.X, pady=5)
        
        self.browse_files_btn = tk.Button(file_btn_frame, text="Browse Files", command=self.browse_files)
        self.browse_files_btn.pack(side=tk.LEFT)
        self.file_count_label = tk.Label(file_btn_frame, text="ยังไม่ได้เลือกไฟล์")
        self.file_count_label.pack(side=tk.LEFT, padx=10)

        # 2. เลือกโฟลเดอร์สำหรับผลลัพธ์ (Output Folder)
        tk.Label(main_frame, text="2. เลือกที่เก็บไฟล์เสียง (Output Folder):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 0))
        out_btn_frame = tk.Frame(main_frame)
        out_btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(out_btn_frame, textvariable=self.output_folder, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(out_btn_frame, text="Browse Folder", command=self.browse_output).pack(side=tk.LEFT, padx=5)

        # Progress Bar
        tk.Label(main_frame, text="ความคืบหน้าภาพรวม (Overall Progress):").pack(anchor=tk.W, pady=(15, 0))
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        # ปุ่มเริ่มทำงาน
        self.start_btn = tk.Button(main_frame, text="เริ่มแปลงไฟล์ (Start Conversion)", 
                                   bg="#dddddd", fg="black", font=("Arial", 11, "bold"),
                                   pady=10, command=self.start_conversion_thread, state='disabled')
        self.start_btn.pack(fill=tk.X, pady=20)

        # ส่วนแสดง Log/Status
        tk.Label(main_frame, text="รายละเอียด (Status Log):").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(main_frame, height=8, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def browse_output(self):
        folder = filedialog.askdirectory(title="เลือกโฟลเดอร์ปลายทาง")
        if folder:
            self.output_folder.set(folder)
            self.check_ready()

    def browse_files(self):
        video_patterns = tuple(f"*{ext}" for ext in self.supported_extensions)
        file_types = [("Video files", video_patterns), ("All files", "*.*")]
        
        files = filedialog.askopenfilenames(title="เลือกไฟล์วิดีโอ", filetypes=file_types)
        if files:
            self.input_files = list(files)
            self.file_count_label.config(text=f"เลือกแล้ว {len(self.input_files)} ไฟล์")
            self.log(f"เลือกไฟล์เข้ามา {len(self.input_files)} ไฟล์")
            
            # ถ้ายังไม่ได้เลือกโฟลเดอร์ปลายทาง ให้ตั้งค่า default เป็นที่เดียวกับไฟล์แรก
            if not self.output_folder.get():
                default_output = os.path.dirname(self.input_files[0])
                self.output_folder.set(default_output)
                self.log(f"ตั้งค่าที่เก็บไฟล์อัตโนมัติ: {default_output}")
                
            self.check_ready()

    def check_ready(self):
        if self.output_folder.get() and self.input_files:
            self.start_btn.config(state='normal', bg="#4CAF50", fg="white")
        else:
            self.start_btn.config(state='disabled', bg="#dddddd", fg="black")

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_conversion_thread(self):
        self.start_btn.config(state='disabled')
        self.browse_files_btn.config(state='disabled')
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()

    def run_conversion(self):
        output_dir = self.output_folder.get()
        total = len(self.input_files)
        
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = total
        
        self.log(f"--- เริ่มต้นการแปลงไฟล์ทั้งหมด {total} ไฟล์ ---")
        
        success_count = 0
        for index, filepath in enumerate(self.input_files, 1):
            filename = os.path.basename(filepath)
            name_without_ext = os.path.splitext(filename)[0]
            mp3_path = os.path.join(output_dir, name_without_ext + ".mp3")
            
            self.log(f"[{index}/{total}] กำลังแปลง: {filename}")
            
            try:
                audioclip = AudioFileClip(filepath)
                audioclip.write_audiofile(mp3_path, logger=None)
                audioclip.close()
                self.log(f"   >> สำเร็จ!")
                success_count += 1
            except Exception as e:
                self.log(f"   !! ผิดพลาด: {e}")
            
            self.progress_bar['value'] = index
            self.root.update_idletasks()

        self.log(f"\n--- เสร็จสิ้น! สำเร็จ {success_count}/{total} ---")
        self.start_btn.config(state='normal')
        self.browse_files_btn.config(state='normal')
        messagebox.showinfo("งานเสร็จสิ้น", f"แปลงไฟล์สำเร็จ {success_count} ไฟล์ครับ!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoToMp3Converter(root)
    root.mainloop()
