import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
import os
from memequiz_api import get_gemini_questions
import re
# ======== Path to CSV File (change to your Excel path if needed) ========
USER_CSV_PATH = r"C:/Users/Teja deep/Desktop/Meme Quiz/user_pass.csv"

# Create the CSV file if it doesn't exist
if not os.path.exists(USER_CSV_PATH):
    with open(USER_CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Username", "Email", "Password"])

# ======== Main Application Class ========
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meme Mania Login")
        self.root.geometry("800x700")  # Increased size
        self.root.minsize(800, 700)
        self.root.configure(bg="#e0eafc")  # Match gradient top color
        self.root.state('zoomed')  # Start maximized

        # Try to load background image
        bg_path = r"C:/Users/Teja deep/Desktop/Meme Quiz/background.png"
        self.bg_image = None
        self.bg_label = None
        if os.path.exists(bg_path):
            try:
                bg_image = Image.open(bg_path)
                self.bg_image = ImageTk.PhotoImage(bg_image)
                self.bg_label = tk.Label(root, image=self.bg_image)
                self.bg_label.place(relwidth=1, relheight=1, x=0, y=0)
            except Exception as e:
                print(f"Warning: Could not load background image: {e}")
        else:
            # Draw a multi-color gradient background using Canvas
            self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0, bd=0)
            self.canvas.place(relwidth=1, relheight=1, x=0, y=0)
            self._draw_gradient(self.canvas, ["#e0eafc", "#a1c4fd", "#c2e9fb", "#fbc2eb", "#fcb69f"])
            self._draw_decorations(self.canvas)

        # Load logo
        logo_image = Image.open(r"C:/Users/Teja deep/Desktop/Meme Quiz/Meme_mania.png")
        logo_image = logo_image.resize((100, 100))
        self.logo = ImageTk.PhotoImage(logo_image)

        self.init_login_page()

    def _draw_gradient(self, canvas, colors):
        # Multi-stop vertical gradient
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        n = len(colors) - 1
        for i in range(n):
            color1 = colors[i]
            color2 = colors[i+1]
            r1, g1, b1 = self.root.winfo_rgb(color1)
            r2, g2, b2 = self.root.winfo_rgb(color2)
            for y in range(i * height // n, (i+1) * height // n):
                ratio = (y - i * height // n) / (height // n)
                nr = int(r1 + (r2 - r1) * ratio)
                ng = int(g1 + (g2 - g1) * ratio)
                nb = int(b1 + (b2 - b1) * ratio)
                color = f'#{nr//256:02x}{ng//256:02x}{nb//256:02x}'
                canvas.create_line(0, y, width, y, fill=color)

    def _draw_decorations(self, canvas):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        # Draw translucent circles
        for (x, y, r, color, alpha) in [
            (width*0.2, height*0.2, 180, '#a1c4fd', 0.18),
            (width*0.8, height*0.3, 120, '#fbc2eb', 0.15),
            (width*0.7, height*0.8, 200, '#fcb69f', 0.13),
            (width*0.3, height*0.7, 140, '#c2e9fb', 0.12),
        ]:
            self._create_circle(canvas, x, y, r, color, alpha)
        # Draw a wave at the bottom
        self._draw_wave(canvas, width, height, '#a1c4fd', 0.18)
        # Draw vignette (soft dark edges)
        self._draw_vignette(canvas, width, height)

    def _create_circle(self, canvas, x, y, r, color, alpha):
        # Simulate alpha by blending with white
        def blend(c, a):
            c = self.root.winfo_rgb(c)
            r = int((1-a)*65535 + a*c[0]) // 256
            g = int((1-a)*65535 + a*c[1]) // 256
            b = int((1-a)*65535 + a*c[2]) // 256
            return f'#{r:02x}{g:02x}{b:02x}'
        fill = blend(color, alpha)
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline="", width=0)

    def _draw_wave(self, canvas, width, height, color, alpha):
        # Simulate alpha by blending with white
        def blend(c, a):
            c = self.root.winfo_rgb(c)
            r = int((1-a)*65535 + a*c[0]) // 256
            g = int((1-a)*65535 + a*c[1]) // 256
            b = int((1-a)*65535 + a*c[2]) // 256
            return f'#{r:02x}{g:02x}{b:02x}'
        fill = blend(color, alpha)
        points = [
            0, height-120,
            width*0.2, height-160,
            width*0.4, height-80,
            width*0.6, height-180,
            width*0.8, height-100,
            width, height-140,
            width, height,
            0, height
        ]
        canvas.create_polygon(points, fill=fill, outline="")

    def _draw_vignette(self, canvas, width, height):
        # Draw a soft vignette using translucent rectangles
        vignette_color = '#000000'
        steps = 20
        for i in range(steps):
            alpha = 0.08 * (i+1) / steps
            margin = int(30 * (steps-i))
            def blend(c, a):
                c = self.root.winfo_rgb(c)
                r = int((1-a)*65535 + a*c[0]) // 256
                g = int((1-a)*65535 + a*c[1]) // 256
                b = int((1-a)*65535 + a*c[2]) // 256
                return f'#{r:02x}{g:02x}{b:02x}'
            fill = blend(vignette_color, alpha)
            canvas.create_rectangle(margin, margin, width-margin, height-margin, outline="", fill=fill)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            if widget not in [getattr(self, 'bg_label', None), getattr(self, 'canvas', None)]:
                widget.destroy()

    def _create_shadowed_frame(self, parent):
        # Standard centered frame with solid white background and subtle border
        main = tk.Frame(parent, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#b0b0b0")
        main.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.36, relheight=0.60)
        return main

    def _styled_entry(self, parent):
        base_font = ("Segoe UI", 14)
        hover_font = ("Segoe UI", 16)
        entry = tk.Entry(parent, font=base_font, bg="#f4f8fb", fg="#222", bd=0, relief="flat", highlightthickness=2, highlightbackground="#b0c4de", highlightcolor="#007acc", insertbackground="#007acc")
        entry.pack(pady=7, ipady=7, ipadx=5, fill='x', padx=20)
        def on_enter(e):
            entry.config(font=hover_font, highlightthickness=3)
        def on_leave(e):
            entry.config(font=base_font, highlightthickness=2)
        entry.bind("<Enter>", on_enter)
        entry.bind("<Leave>", on_leave)
        return entry

    def _styled_label(self, parent, text):
        base_font = ("Segoe UI", 13, "bold")
        hover_font = ("Segoe UI", 15, "bold")
        label = tk.Label(parent, text=text, bg="#ffffff", fg="#007acc", font=base_font)
        def on_enter(e):
            label.config(font=hover_font)
        def on_leave(e):
            label.config(font=base_font)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        return label

    def _styled_button(self, parent, text, command, primary=True):
        base_font = ("Segoe UI", 13, "bold")
        hover_font = ("Segoe UI", 15, "bold")
        color = "#007acc" if primary else "#ffffff"
        fg = "#ffffff" if primary else "#007acc"
        btn = tk.Button(parent, text=text, command=command, bg=color, fg=fg, font=base_font, bd=0, relief="flat", activebackground="#005f99", activeforeground="#fff", cursor="hand2", highlightthickness=0)
        btn.pack(pady=(12 if primary else 0, 0), ipadx=5, ipady=5, fill='x', padx=20)
        # Add hover effect (color and enlarge)
        def on_enter(e):
            btn['bg'] = "#005f99" if primary else "#e6f2fa"
            btn.config(font=hover_font, ipadx=10, ipady=8)
        def on_leave(e):
            btn['bg'] = color
            btn.config(font=base_font, ipadx=5, ipady=5)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _custom_messagebox(self, title, message, kind="info"):
        # kind: 'info' or 'error'
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg="#ffffff")
        popup.resizable(False, False)
        popup.geometry("400x200")
        popup.update_idletasks()
        # Center the popup
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        popup.geometry(f"+{x}+{y}")

        # Icon
        icon_text = "\u2139" if kind == "info" else "\u26A0"
        icon_color = "#007acc" if kind == "info" else "#d9534f"
        icon_label = tk.Label(popup, text=icon_text, font=("Segoe UI", 40), fg=icon_color, bg="#ffffff")
        icon_label.pack(pady=(20, 0))

        # Message
        msg_label = tk.Label(popup, text=message, font=("Segoe UI", 13), bg="#ffffff", fg="#222", wraplength=340, justify="center")
        msg_label.pack(pady=(10, 0), padx=20)

        # OK Button
        def close():
            popup.destroy()
        ok_btn = tk.Button(popup, text="OK", command=close, bg="#007acc", fg="#fff", font=("Segoe UI", 12, "bold"), bd=0, relief="flat", activebackground="#005f99", activeforeground="#fff", cursor="hand2", highlightthickness=0)
        ok_btn.pack(pady=20, ipadx=10, ipady=5)
        ok_btn.focus_set()
        popup.bind("<Return>", lambda e: close())
        popup.bind("<Escape>", lambda e: close())
        popup.wait_window()

    # ======== Login Page ========
    def init_login_page(self):
        self.clear_frame()
        frame = self._create_shadowed_frame(self.root)
        tk.Label(frame, image=self.logo, bg="#ffffff").pack(pady=(10, 0))
        self._styled_label(frame, "Username").pack(pady=(18, 0))
        self.login_username = self._styled_entry(frame)
        self._styled_label(frame, "Password").pack(pady=(10, 0))
        self.login_password = self._styled_entry(frame)
        self.login_password.config(show="*")
        self._styled_button(frame, "Login", self.login_user, primary=True)
        self._styled_button(frame, "Sign Up", self.init_signup_page, primary=False)

    # ======== Signup Page ========
    def init_signup_page(self):
        self.clear_frame()
        frame = self._create_shadowed_frame(self.root)
        tk.Label(frame, image=self.logo, bg="#ffffff").pack(pady=(10, 0))
        self._styled_label(frame, "Username").pack(pady=(18, 0))
        self.signup_username = self._styled_entry(frame)
        self._styled_label(frame, "Email").pack(pady=(10, 0))
        self.signup_email = self._styled_entry(frame)
        self._styled_label(frame, "Password").pack(pady=(10, 0))
        self.signup_password = self._styled_entry(frame)
        self.signup_password.config(show="*")
        self._styled_button(frame, "Sign Up", self.signup_user, primary=True)
        self._styled_button(frame, "Back to Login", self.init_login_page, primary=False)
        tk.Label(frame, text="", bg="#ffffff").pack(pady=20)  # Extra space at the bottom

    # ======== Login Logic ========
    def login_user(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        if not username or not password:
            self._custom_messagebox("Error", "Please fill in all fields.", kind="error")
            return
        with open(USER_CSV_PATH, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Username"] == username and row["Password"] == password:
                    self._custom_messagebox("Success", f"Welcome back, {username}!", kind="info")
                    self.show_category_page()
                    return
        self._custom_messagebox("Error", "Incorrect username or password.", kind="error")

    def show_category_page(self):
        self.clear_frame()
        frame = self._create_shadowed_frame(self.root)
        tk.Label(frame, text="Choose a Category", bg="#ffffff", fg="#007acc", font=("Segoe UI", 22, "bold")).pack(pady=(30, 8))
        tk.Label(frame, text="What do you want to play?", bg="#ffffff", fg="#555", font=("Segoe UI", 13, "italic")).pack(pady=(0, 24))
        self._category_button(frame, "🎬  Tollywood", lambda: self.start_quiz("Tollywood"))
        self._category_button(frame, "💻  Computer Science", lambda: self.start_quiz("Computer Science"))
        self._category_button(frame, "🏏  Cricket", lambda: self.start_quiz("Cricket"))

    def start_quiz(self, category):
        self.quiz_questions = get_gemini_questions(category)
        if not self.quiz_questions:
            self._custom_messagebox("Error", f"No questions could be generated for {category}.", kind="error")
            self.show_category_page()
            return
        self.quiz_category = category
        self.quiz_index = 0
        self.quiz_score = 0
        self.wrong_answers = []  # Track wrong answers for review
        self.show_question()

    def show_question(self):
        self.clear_frame()
        frame = self._create_shadowed_frame(self.root)
        q = self.quiz_questions[self.quiz_index]
        tk.Label(frame, text=f"Q{self.quiz_index+1}: {q['question']}", bg="#ffffff", fg="#222", font=("Segoe UI", 15, "bold"), wraplength=400, justify="left").pack(pady=(30, 18), padx=10)
        self.selected_option = tk.StringVar()
        for opt in q['options']:
            rb = tk.Radiobutton(frame, text=opt, variable=self.selected_option, value=opt, bg="#ffffff", fg="#007acc", font=("Segoe UI", 13), selectcolor="#e0eafc", activebackground="#e0eafc", anchor="w", padx=20, pady=8, indicatoron=1)
            rb.pack(fill='x', padx=30, pady=4)
        btn = tk.Button(frame, text="Next", command=self.next_question, bg="#007acc", fg="#fff", font=("Segoe UI", 13, "bold"), bd=0, relief="flat", activebackground="#005f99", activeforeground="#fff", cursor="hand2", highlightthickness=0)
        btn.pack(pady=30, ipadx=10, ipady=6)

    def next_question(self):
        q = self.quiz_questions[self.quiz_index]
        selected = self.selected_option.get()
        if not selected:
            self._custom_messagebox("Error", "Please select an option before proceeding.", kind="error")
            return
        if selected == q['answer']:
            self.quiz_score += 1
        else:
            # Store question, selected, and correct answer for review
            self.wrong_answers.append({
                'question': q['question'],
                'options': q['options'],
                'your_answer': selected,
                'correct_answer': q['answer']
            })
        self.quiz_index += 1
        if self.quiz_index < len(self.quiz_questions):
            self.show_question()
        else:
            self.show_score()

    def show_score(self):
        self.clear_frame()
        frame = self._create_shadowed_frame(self.root)
        tk.Label(frame, text="Quiz Completed!", bg="#ffffff", fg="#007acc", font=("Segoe UI", 22, "bold")).pack(pady=(40, 10))
        # Determine which image to show based on score
        if self.quiz_score <= 3:
            img_path = "0-3.jpg"
        elif self.quiz_score <= 6:
            img_path = "4-6.jpg"
        else:
            img_path = "7-10.jpg"
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img = img.resize((250, 250))
            img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(frame, image=img_tk, bg="#ffffff")
            img_label.image = img_tk  # Keep reference
            img_label.pack(pady=(0, 20))
        tk.Label(frame, text=f"Your Score: {self.quiz_score} / {len(self.quiz_questions)}", bg="#ffffff", fg="#222", font=("Segoe UI", 18, "bold")).pack(pady=(0, 30))
        if self.wrong_answers:
            self._styled_button(frame, "Review", self.show_review_page, primary=True)
            tk.Label(frame, text="", bg="#ffffff").pack(pady=5)  # Spacer
        self._styled_button(frame, "Back to Categories", self.show_category_page, primary=False)

    def show_review_page(self):
        self.clear_frame()
        frame = self._create_shadowed_frame(self.root)
        tk.Label(frame, text="Review Wrong Answers", bg="#ffffff", fg="#d9534f", font=("Segoe UI", 20, "bold")).pack(pady=(30, 10))
        if not self.wrong_answers:
            tk.Label(frame, text="No wrong answers!", bg="#ffffff", fg="#222", font=("Segoe UI", 14)).pack(pady=20)
            self._styled_button(frame, "Back to Categories", self.show_category_page, primary=True)
            return
        # Show the first wrong answer, with navigation
        self.review_index = 0
        self._show_single_review(frame)

    def _show_single_review(self, frame):
        wa = self.wrong_answers[self.review_index]
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") == "Review Wrong Answers":
                continue  # Keep the title
            widget.destroy()
        q_lbl = tk.Label(frame, text=f"Q: {wa['question']}", bg="#ffffff", fg="#222", font=("Segoe UI", 14, "bold"), wraplength=400, justify="left")
        q_lbl.pack(pady=(10, 8), padx=10)
        for opt in wa['options']:
            color = "#d9534f" if opt == wa['your_answer'] else ("#5cb85c" if opt == wa['correct_answer'] else "#007acc")
            tk.Label(frame, text=opt, bg="#ffffff", fg=color, font=("Segoe UI", 13), anchor="w", padx=20, pady=4, wraplength=400, justify="left").pack(fill='x', padx=30)
        tk.Label(frame, text=f"Your answer: {wa['your_answer']}", bg="#ffffff", fg="#d9534f", font=("Segoe UI", 12, "italic")).pack(pady=(10, 0))
        tk.Label(frame, text=f"Correct answer: {wa['correct_answer']}", bg="#ffffff", fg="#5cb85c", font=("Segoe UI", 12, "italic")).pack(pady=(0, 10))
        nav_frame = tk.Frame(frame, bg="#ffffff")
        nav_frame.pack(pady=10)
        if self.review_index > 0:
            tk.Button(nav_frame, text="Previous", command=lambda: self._review_nav(frame, -1), bg="#007acc", fg="#fff", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", activebackground="#005f99", activeforeground="#fff", cursor="hand2", highlightthickness=0).pack(side='left', padx=10)
        if self.review_index < len(self.wrong_answers) - 1:
            tk.Button(nav_frame, text="Next", command=lambda: self._review_nav(frame, 1), bg="#007acc", fg="#fff", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", activebackground="#005f99", activeforeground="#fff", cursor="hand2", highlightthickness=0).pack(side='left', padx=10)
        self._styled_button(frame, "Back to Categories", self.show_category_page, primary=True)

    def _review_nav(self, frame, direction):
        self.review_index += direction
        self._show_single_review(frame)

    def _category_button(self, parent, text, command):
        base_font = ("Segoe UI", 17, "bold")
        hover_font = ("Segoe UI", 20, "bold")
        btn = tk.Button(parent, text=text, command=command, bg="#f4f8fb", fg="#007acc", font=base_font, bd=0, relief="flat", activebackground="#e0eafc", activeforeground="#005f99", cursor="hand2", highlightthickness=0)
        btn.pack(pady=18, ipadx=10, ipady=12, fill='x', padx=30)
        btn.config(borderwidth=2, highlightbackground="#a1c4fd", highlightcolor="#a1c4fd")
        # Add hover effect (enlarge and color change)
        def on_enter(e):
            btn.config(font=hover_font, bg="#a1c4fd", fg="#fff", borderwidth=3)
        def on_leave(e):
            btn.config(font=base_font, bg="#f4f8fb", fg="#007acc", borderwidth=2)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ======== Signup Logic ========
    def signup_user(self):
        username = self.signup_username.get().strip()
        email = self.signup_email.get().strip()
        password = self.signup_password.get().strip()
        if not username or not email or not password:
            self._custom_messagebox("Error", "Please fill in all fields.", kind="error")
            return
        with open(USER_CSV_PATH, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Username"] == username:
                    self._custom_messagebox("Error", "Username already exists.", kind="error")
                    return
        with open(USER_CSV_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, email, password])
            self._custom_messagebox("Success", "Account created! Please log in.", kind="info")
            self.init_login_page()

# ======== Run the App ========
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
