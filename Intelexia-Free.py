#!/usr/bin/env python3
from tkinter import ttk,  Menu
import numpy as np
from PIL import Image, ImageTk
import json
import openvino_genai as ov_genai
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import Toplevel, simpledialog
import time
import queue
import threading

# Globals
streamer_queue = queue.Queue()

# Config
with open("config.json", "r") as json_file:
    config = json.load(json_file)
    systemPrompt = config["systemPrompt"]
    UserName = config["UserName"]
    Model = config["Model"]
    LoraModel = config["LoraModel"]
    LLMDevice = config["LLMDevice"]
    LoraDevice = config["LoraDevice"]


# Exit
def exit_app():
    print("[+] Exit!")
    window.destroy()

# Streamer
def streamer(subword):
    streamer_queue.put(subword)

# Clean input
def delete_input():
    inputBox.delete('1.0', tk.END)

# Load model
def load_model():
    global pipe
    # Initialize your model here
    model_path = "Models/"+Model
    pipe = ov_genai.LLMPipeline(model_path, LLMDevice, MAX_PROMPT_LEN=1024, MIN_RESPONSE_LEN=128, MAX_LEN_OUTPUT =1024)


# Update output
def update_output():
    outputBox.config(state=tk.NORMAL)
    try:
        while True:
            subword = streamer_queue.get_nowait()
            outputBox.insert(tk.END, subword)
            outputBox.see(tk.END)
    except queue.Empty:
        pass
    window.after(45, update_output)# Schedule next check
    outputBox.config(state=tk.DISABLED)

# Chat with LLM
def chat():
    user_input = inputBox.get(1.0, tk.END)
    if user_input is None:
        return
    window.after(0, lambda: status.config(text="[+] Loading Inference...", bg="red"))
    def run():
        start_time = time.time()
        outputBox.configure(state=tk.NORMAL)
        outputBox.insert(tk.INSERT, "\n")
        outputBox.insert(tk.INSERT, "[-]"+UserName + ": ")
        outputBox.insert(tk.INSERT, user_input)
        outputBox.see('end')
        delete_input()
        prompt = systemPrompt + user_input
        if not prompt:
            window.after(0, lambda: status.config(text="[!] Please enter a prompt.", bg='red'))
            return
        config_llm = ov_genai.GenerationConfig(max_new_tokens=1024, top_k=50, top_p=0.9)
        pipe.start_chat()
        outputBox.insert(tk.INSERT, "[+]Intelexia: ")
        pipe.generate(prompt, config_llm, streamer)
        pipe.finish_chat()
        outputBox.configure(state=tk.DISABLED)
        end_time = time.time()
        execution_time = end_time - start_time
        window.after(0, lambda: status.config(text=f"[+] Inference Time: {execution_time:.2f} seconds", bg='green'))
    threading.Thread(target=run, daemon=True).start()

#Lora class
class Generator(ov_genai.Generator):
    def __init__(self, seed, mu=0.0, sigma=1.0):
        ov_genai.Generator.__init__(self)
        np.random.seed(seed)
        self.mu = mu
        self.sigma = sigma
    def next(self):
        return np.random.normal(self.mu, self.sigma)

#Lora
def launch_lora():
    image_prompt = simpledialog.askstring(title="LORA", prompt="Enter prompt")
    if image_prompt is None:
        return
    window.after(0, lambda: status.config(text="[+] Loading Lora...", bg="red"))
    def run():
        start_time = time.time()
        pipe_lora = ov_genai.Text2ImagePipeline("Models/"+LoraModel, LoraDevice)
        image_tensor = pipe_lora.generate(
            image_prompt,
            width=512,
            height=512,
            num_inference_steps=20,
            num_images_per_prompt=1,
            generator=Generator(42)
        )
        image = Image.fromarray(image_tensor.data[0])
        image.save("Images/"+image_prompt+".bmp")# Define the host path on Main
        # Display image in a new top-level window
        image_window = Toplevel(window)
        image_window.title("Generated Image")
        image_window.configure(bg="#2a2d2e")
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(image_window, image=photo, bg="#2a2d2e")
        label.image = photo  # Keep reference to prevent garbage collection
        label.pack(padx=10, pady=10)
        end_time = time.time()
        execution_time = end_time - start_time
        window.after(0, lambda: status.config(text=f"[+] Lora Time: {execution_time:.2f} seconds", bg='green'))
    threading.Thread(target=run, daemon=True).start()

## Tkinter
# Main Window
window = tk.Tk()
window.title("Intelexia-Free")
window.geometry("600x1024")
window.configure(bg="#2a2d2e")
window.iconphoto(False, tk.PhotoImage(file="robot.png"))
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)
window.minsize(450, 800)

# Status:
status = tk.Label(window, width=94, text="[+] Model loaded OK!",bg='green')
# Out Box
outputBox = ScrolledText(window, width=50, height=20, wrap='word', bg="#373b41", fg="white", state='disabled')

# In Box
inputBox = ScrolledText(window, width=81, height=5, wrap='word', bg="#373b40", fg="white")

# File bar
menubar = Menu(window, bg="#373b41", fg="white")
file_menu = Menu(menubar, tearoff=False, bg="#373b41", fg="white")
file_menu.add_command(label="Exit", command=exit_app)
menubar.add_cascade(label="File", menu=file_menu)

# Add the menubar to the root window
window.config(menu=menubar)

# Bindings
inputBox.bind("<Return>", lambda event: chat())

# Buttons
generate_button1 = ttk.Button(
    window,
    text="Chat",
    command=chat,
    style="Custom.TButton")

generate_button2 = ttk.Button(
    window,
    text="Lora",
    command=launch_lora,
    style="Custom.TButton")

# Grid
outputBox.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")
inputBox.grid(row=4, column=0, sticky="nsew")
generate_button1.grid(row=4, column=1, sticky="nsw")
generate_button2.grid(row=5, column=1, sticky="nsw")
status.grid(row=5, column=0, rowspan=2, sticky="ew")

# Main
def main():
    load_model()
    window.after(50, update_output)
    window.mainloop()

if '__main__' == __name__:
    main()
