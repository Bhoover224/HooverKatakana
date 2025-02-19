import tkinter as tk
from tkinter import Toplevel, Checkbutton, IntVar, Label, Entry, Button, Frame
import random
import configparser
import os
from collections import deque

# Katakana dictionary grouped
katakana_groups = {
    'Vowels': {'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o'},
    'K Group': {'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko'},
    'S Group': {'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so'},
    'T Group': {'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to'},
    'N Group': {'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no'},
    'H Group': {'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho'},
    'M Group': {'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo'},
    'Y Group': {'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo'},
    'R Group': {'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro'},
    'W Group': {'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n'}
}

CONFIG_FILE = 'katakana_config.cfg'

class KatakanaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Katakana Learning App")
        self.root.configure(bg='black')
        self.root.geometry("1920x1020")

        self.selected_katakana = {key: IntVar(value=1) for group in katakana_groups.values() for key in group.keys()}
        self.katakana_list = list(self.selected_katakana.keys())

        self.previous_katakana = ''  # To track the previous katakana
        self.input_enabled = True  # Flag to enable/disable input
        self.katakana_queue = deque()  # Queue to evenly distribute characters

        self.load_config()

        self.current_katakana = ''
        self.answer_label = None

        self.katakana_label = Label(root, text='', font=('Helvetica', 128), fg='white', bg='black')
        self.katakana_label.pack(pady=40)

        self.entry = Entry(root, font=('Helvetica', 48), bg='black', fg='white', insertbackground='white')
        self.entry.pack(pady=20)
        self.entry.bind('<Return>', self.check_answer)

        self.settings_button = Button(root, text="Settings", command=self.open_settings, bg='black', fg='white', font=('Helvetica', 32))
        self.settings_button.pack(pady=20)

        self.exit_button = Button(root, text="Exit", command=self.root.quit, bg='black', fg='white', font=('Helvetica', 32))
        self.exit_button.pack(pady=20)

        self.next_katakana()

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE, encoding='utf-8')
            for key in self.selected_katakana.keys():
                if key in config['Katakana']:
                    self.selected_katakana[key].set(int(config['Katakana'][key]))

    def save_config(self):
        config = configparser.ConfigParser()
        config['Katakana'] = {key: str(var.get()) for key, var in self.selected_katakana.items()}
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except UnicodeEncodeError as e:
            print(f"Encoding Error: {e}")

    def next_katakana(self):
        if self.answer_label:
            self.answer_label.destroy()

        active_katakana = [k for k, v in self.selected_katakana.items() if v.get() == 1]

        if not self.katakana_queue or any(k not in self.katakana_queue for k in active_katakana):
            # Refill the queue if it's empty or new characters are active
            self.katakana_queue = deque(active_katakana)
            random.shuffle(self.katakana_queue)

        self.current_katakana = self.katakana_queue.popleft()
        self.katakana_label.config(text=self.current_katakana)

        self.entry.delete(0, tk.END)
        self.input_enabled = True  # Re-enable input

    def check_answer(self, event):
        if not self.input_enabled:
            return  # Ignore input if disabled

        user_input = self.entry.get().strip().lower()
        correct_answer = next((v for group in katakana_groups.values() for k, v in group.items() if k == self.current_katakana), '')

        if user_input == correct_answer:
            self.next_katakana()
        else:
            if self.answer_label:
                self.answer_label.destroy()
            self.answer_label = Label(self.root, text=f"Answer: {correct_answer}", fg='red', font=('Helvetica', 36), bg='black')
            self.answer_label.pack()
            self.input_enabled = False  # Disable input during pause
            self.root.after(2000, self.next_katakana)

    def open_settings(self):
        settings_window = Toplevel(self.root)
        settings_window.title("Select Katakana")
        settings_window.configure(bg='black')
        settings_window.geometry("2000x800")  # Wider settings window

        def on_close():
            self.save_config()
            settings_window.destroy()
            self.next_katakana()  # Move to next character after closing

        settings_window.protocol("WM_DELETE_WINDOW", on_close)
        settings_window.bind('<Escape>', lambda e: on_close())  # Bind Esc key to close

        def update_group_var(group_var, group):
            group_var.set(all(self.selected_katakana[k].get() for k in group))

        for idx, (group_name, group) in enumerate(katakana_groups.items()):
            frame = Frame(settings_window, bg='black')
            frame.grid(row=0, column=idx, padx=20, pady=20, sticky='n')

            group_var = IntVar()
            update_group_var(group_var, group)

            def toggle_group(var=group_var, g=group):
                for katakana in g:
                    self.selected_katakana[katakana].set(var.get())
                update_group_var(var, g)

            group_checkbox = Checkbutton(frame, text=group_name, variable=group_var, command=lambda g=group: toggle_group(group_var, g), fg='white', bg='black', selectcolor='black', font=('Helvetica', 24))
            group_checkbox.pack(anchor='w')

            for katakana, romaji in group.items():
                chk = Checkbutton(frame, text=f"{katakana} ({romaji})", variable=self.selected_katakana[katakana], fg='white', bg='black', selectcolor='black', font=('Helvetica', 20), command=lambda g=group: update_group_var(group_var, g))
                chk.pack(anchor='w')

        exit_button = Button(settings_window, text="Exit", command=on_close, bg='black', fg='white', font=('Helvetica', 24))
        exit_button.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = KatakanaApp(root)
    root.mainloop()
