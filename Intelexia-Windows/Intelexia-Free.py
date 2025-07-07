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
import os

# Globals
streamer_queue = queue.Queue()

def clean_response(response):
    """Clean up AI response to remove repetition and unwanted tokens"""
    if not response:
        return ""

    # Remove special tokens
    response = response.replace("<|assistant|>", "").replace("<|system|>", "").replace("<|user|>", "")
    response = response.replace("</s>", "").replace("<s>", "")
    response = response.strip()

    # Check for obvious repetition patterns
    lines = response.split('\n')
    cleaned_lines = []
    seen_lines = set()

    for line in lines:
        line = line.strip()
        if not line:
            cleaned_lines.append("")
            continue

        # Check for exact line repetition
        if line in seen_lines and len(line) > 20:
            # Skip this line if it's a repetition of a longer line
            continue

        cleaned_lines.append(line)
        if len(line) > 20:  # Only track longer lines for repetition detection
            seen_lines.add(line)

    # Join lines back
    result = '\n'.join(cleaned_lines)

    # Remove excessive repetition within the same line
    words = result.split()
    if len(words) > 10:
        # Check for word-level repetition
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Only count meaningful words
                word_counts[word] = word_counts.get(word, 0) + 1

        # If any word appears more than 4 times, it's likely repetitive
        max_repetition = max(word_counts.values()) if word_counts else 0
        if max_repetition > 4:
            # Find the most repeated word and truncate at its excessive repetition
            most_repeated = max(word_counts, key=word_counts.get)
            words_clean = []
            repeat_count = 0
            for word in words:
                if word == most_repeated:
                    repeat_count += 1
                    if repeat_count > 2:  # Allow up to 2 repetitions
                        # Try to end at a sentence boundary
                        if len(words_clean) > 0 and words_clean[-1].endswith('.'):
                            break
                        elif len(words_clean) > 10:  # Or if we have enough content
                            break
                words_clean.append(word)
            result = ' '.join(words_clean)

            # Ensure it ends properly
            if result and not result.endswith(('.', '!', '?', '```')):
                # Try to find the last sentence ending
                last_sentence_end = max(
                    result.rfind('.'),
                    result.rfind('!'),
                    result.rfind('?')
                )
                if last_sentence_end > len(result) * 0.7:  # If we can keep most of the content
                    result = result[:last_sentence_end + 1]

    # Ensure response doesn't end abruptly in the middle of a code block or sentence
    if '```' in result:
        # Count code block markers
        code_blocks = result.count('```')
        if code_blocks % 2 == 1:  # Odd number means unclosed code block
            result += '\n```'

    return result.strip()

# Config
with open("config.json", "r") as json_file:
    config = json.load(json_file)
    systemPrompt = config["systemPrompt"]
    UserName = config["UserName"]
    BotName = config["BotName"]  # Fix: Add missing BotName variable
    Model = config["Model"]
    LoraModel = config["LoraModel"]
    LLMDevice = config["LLMDevice"]
    LoraDevice = config["LoraDevice"]

#History
chat_history = []
max_turns = 10

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
    try:
        # Initialize your model here - use os.path.join for cross-platform compatibility
        model_path = os.path.join("Models", Model)

        # Check if model directory exists
        if not os.path.exists(model_path):
            print(f"[!] Model directory not found: {model_path}")
            print(f"[!] Please download the model first using the instructions in README.md")
            return False

        # Create pipeline with improved configuration for Windows compatibility
        pipe = ov_genai.LLMPipeline(model_path, LLMDevice)
        print(f"[+] Model loaded successfully from: {model_path}")
        return True
    except Exception as e:
        print(f"[!] Error loading model: {str(e)}")
        print(f"[!] Make sure OpenVINO and Intel NPU drivers are properly installed")
        return False


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
    user_input = inputBox.get(1.0, tk.END).strip()
    if not user_input:
        return
    window.after(0, lambda: status.config(text="[+] Loading Inference...", bg="red"))

    def run():
        global chat_history
        start_time = time.time()
        outputBox.configure(state=tk.NORMAL)
        outputBox.insert(tk.INSERT, "\n[-]" + UserName + ": " + user_input + "\n")
        outputBox.see('end')
        delete_input()
        chat_history.append(f"{UserName}: {user_input}")
        if len(chat_history) > max_turns * 2:
            chat_history = chat_history[-max_turns * 2:]
        # Format prompt for TinyLlama chat template
        conversation_history = "\n".join(chat_history[-6:])  # Limit to last 6 exchanges
        full_prompt = f"<|system|>\n{systemPrompt}</|system|>\n{conversation_history}\n<|assistant|>\n"
        if not full_prompt:
            window.after(0, lambda: status.config(text="[!] Please enter a prompt.", bg='red'))
            return
        # Optimized generation config for TinyLlama - balance between completeness and quality
        config_llm = ov_genai.GenerationConfig(
            max_new_tokens=384,          # Balanced: enough for complete responses, not too much for repetition
            top_k=40,                    # Slightly more restrictive for better quality
            top_p=0.85,                  # Slightly lower for more focused responses
            temperature=0.8,             # Higher temperature for more variety
            repetition_penalty=1.15,     # Stronger repetition penalty for TinyLlama
            do_sample=True,              # Enable sampling for variety
            eos_token_id=2               # Ensure proper stopping
        )
        pipe.start_chat()
        outputBox.insert(tk.INSERT, "[+]" + BotName + ": ")
        response = pipe.generate(full_prompt, config_llm, streamer)
        pipe.finish_chat()

        # Clean up response to remove repetition and unwanted tokens
        cleaned_response = clean_response(response)
        outputBox.insert(tk.INSERT, cleaned_response + "\n")
        outputBox.configure(state=tk.DISABLED)
        chat_history.append(f"{BotName}: {cleaned_response}")
        if len(chat_history) > max_turns * 2:
            chat_history = chat_history[-max_turns * 2:]
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
        try:
            start_time = time.time()

            # Use os.path.join for cross-platform compatibility
            lora_model_path = os.path.join("Models", LoraModel)

            # Check if model directory exists
            if not os.path.exists(lora_model_path):
                print(f"[!] LoRA model directory not found: {lora_model_path}")
                window.after(0, lambda: status.config(text="[!] LoRA model not found", bg='red'))
                return

            pipe_lora = ov_genai.Text2ImagePipeline(lora_model_path, LoraDevice)
            image_tensor = pipe_lora.generate(
                image_prompt,
                width=512,
                height=512,
                num_inference_steps=20,
                num_images_per_prompt=1,
                generator=Generator(42)
            )
            image = Image.fromarray(image_tensor.data[0])

            # Create Images directory if it doesn't exist
            os.makedirs("Images", exist_ok=True)

            # Sanitize filename for Windows compatibility
            safe_filename = "".join(c for c in image_prompt if c.isalnum() or c in (' ', '-', '_')).rstrip()
            image_path = os.path.join("Images", f"{safe_filename}.bmp")
            image.save(image_path)

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
        except Exception as e:
            print(f"[!] Error in LoRA generation: {str(e)}")
            window.after(0, lambda: status.config(text=f"[!] LoRA Error: {str(e)}", bg='red'))
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
inputBox.bind("<Return>", lambda _: chat())

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
    # Create necessary directories
    os.makedirs("Models", exist_ok=True)
    os.makedirs("Images", exist_ok=True)

    # Load model and check if successful
    if not load_model():
        # Show error dialog and continue with limited functionality
        status.config(text="[!] Model loading failed - check console for details", bg='red')

    window.after(50, update_output)
    window.mainloop()

if '__main__' == __name__:
    main()
