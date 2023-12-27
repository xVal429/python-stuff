import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import shutil
import send2trash
from datetime import datetime
import math

# You'll need pillow & send2trash. Run the pip-install.cmd

class ImageSorter:
    # color config, by default they're set to a dark theme
    BACKGROUND_COLOR = '#202020'
    FOREGROUND_COLOR = '#ffffff'

    # you will probably never need this, but if you want to test the program without actually moving or deleting files, you can set this to "True"
    DEVTEST = False

    def __init__(self, master):
        self.master = master
        self.master.configure(background=self.BACKGROUND_COLOR)
        self.canvas = tk.Canvas(master, width=500, height=500, bg=self.BACKGROUND_COLOR)
        self.canvas.pack()
        self.index = 0
        self.images = []
        self.output_dirs = [None] * 9
        self.create_image_label()
        self.select_source_directory()
        self.create_buttons()
        self.select_number_of_directories()
        self.bind_keys()
        self.action_stack = []

    def bind_keys(self):
        for i in range(9):
            self.master.bind(str(i+1), self.create_move_image_callback(i))
        self.master.bind('<Delete>', lambda event: self.process_image('delete'))
        self.master.bind('<BackSpace>', lambda event: self.undo())

    def create_move_image_callback(self, i):
        return lambda event: self.process_image('move', self.output_dirs[i]) if self.output_dirs[i] is not None else None

    def create_buttons(self):
        self.start_button = tk.Button(self.master, text="Start", command=self.start, bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        self.start_button.pack(side=tk.LEFT)
        self.move_buttons = [tk.Button(self.master, text=f"Move to directory {i+1}", command=lambda i=i: self.process_image('move', self.output_dirs[i]), bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR) for i in range(9)]
        self.button_del = tk.Button(self.master, text="[DEL] Delete", command=lambda: self.process_image('delete'), bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        self.button_undo = tk.Button(self.master, text="[BACKSPACE] Undo", command=self.undo, bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
    
    def manage_buttons(self, action):
        if action == 'show':
            for button in self.move_buttons[:self.num_dirs]:
                button.pack(side=tk.LEFT)
            self.button_del.pack(side=tk.LEFT)
        elif action == 'hide':
            for button in self.move_buttons:
                button.pack_forget()
            self.button_del.pack_forget()
            self.button_undo.pack_forget()

    def select_number_of_directories(self):
        self.num_dirs = simpledialog.askinteger("Number of directories", "Enter the number of output directories (2-9):", minvalue=2, maxvalue=9)
        self.manage_buttons('show')
        for i in range(self.num_dirs):
            self.select_output_directory(i)
        self.start()

    def select_output_directory(self, i):
        self.output_dirs[i] = filedialog.askdirectory(title=f"Select output {i+1} directory", initialdir=os.getcwd())
        if not self.output_dirs[i]:
            messagebox.showerror("No directory selected", f"You must select an output directory {i+1}.")
            self.select_output_directory(i)
        else:
            self.move_buttons[i].config(text=f"[{i+1}] Move to {os.path.basename(self.output_dirs[i])}")

    def create_image_label(self):
        self.image_label = tk.Label(self.master, text="", bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        self.image_label.pack(side=tk.TOP, anchor=tk.S)

    def start(self):
        with os.scandir(self.source_dir) as entries:
            self.images = [entry.path for entry in entries if entry.is_file()]
        if self.images:
            self.process_image('show')
            self.manage_buttons('show')
        else:
            messagebox.showinfo("No images", "There are no images in the source directory.")
        self.start_button.pack_forget()

    def select_source_directory(self):
        self.source_dir = filedialog.askdirectory(title="Select source directory", initialdir=os.getcwd())
        if not self.source_dir:
            messagebox.showerror("No directory selected", "You must select a source directory.")
            self.select_source_directory()

    def process_image(self, action, output_dir=None):
        image_path = self.images[self.index]
        if action == 'show':
            image = Image.open(image_path)
            image.thumbnail((500, 500))
            photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(250, 250, image=photo)
            self.canvas.image = photo

            # Get image info
            stat_info = os.stat(image_path)
            date_created = datetime.fromtimestamp(os.path.getctime(image_path)).strftime('%d/%m/%Y %H:%M:%S')
            #date_modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
            file_name = os.path.basename(image_path)
            size = self.convert_size(stat_info.st_size)
            extension = os.path.splitext(image_path)[1]

            # Display image info
            info_text = f"File Name: {file_name}\nDate Created: {date_created}\nSize: {size}\nExtension: {extension}"
            self.image_label.config(text=info_text)

        elif action in ['move', 'delete'] and os.path.exists(image_path):
            if not self.DEVTEST:
                if action == 'move':
                    shutil.move(image_path, output_dir)
                    self.action_stack.append(('move', image_path, output_dir))
                else:  # action == 'delete'
                    relative_path = os.path.relpath(image_path)
                    send2trash.send2trash(relative_path)
                    self.action_stack.append(('delete', image_path))
            self.button_undo.pack(side=tk.LEFT)
            self.process_image('next')
        elif action == 'next':
            self.index += 1
            if self.index < len(self.images):
                self.process_image('show')
            else:
                self.canvas.delete("all")
                messagebox.showinfo("Finished", "All images have been processed.")
                self.manage_buttons('hide')
                self.image_label.config(text="No more images!")

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0 bytes"
        size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
    
    def undo(self):
        if self.action_stack:
            action, image_path, *rest = self.action_stack.pop()
            if action == 'move':
                output_dir = rest[0]
                shutil.move(os.path.join(output_dir, os.path.basename(image_path)), image_path)
            else:  # action == 'delete'
                messagebox.showinfo("oopsie :(", "I do not know how to undo deletions. \nIt is in your recycling bin, though.")
                return
            self.index -= 1
            self.process_image('show')

root = tk.Tk()
app = ImageSorter(root)
root.mainloop()