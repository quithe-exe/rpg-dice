import random
import time
from datetime import datetime
import customtkinter as ctk

# CustomTkinter Appearance Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("theme/theme.json")

# Clean & Smooth Font Family
SMOOTH_FONT = ("Segoe UI", "Trebuchet MS", "Helvetica", "sans-serif")
MONO_FONT = ("Consolas", "Courier New", "monospace")

# Detailed Lying Cat ASCII Art
ASCII_CAT_DETAILED = r"""
      ,\
          \\\,_
           \` ,\
       __,.-" =__)
  ."        )
,_/   ,    \/\_
\_|    )_-\ \_-`
`-----` `--`
"""


class SmoothRollingDiceCard(ctk.CTkFrame):
    """Dice card utilizing sub-pixel smooth rendering and Cubic Ease-Out curve."""

    def __init__(self, master, sides, final_val, raw_val, was_boosted, **kwargs):
        super().__init__(
            master,
            width=60,
            height=60,
            corner_radius=10,
            border_width=2,
            border_color="#45475a",
            fg_color="#313244",
            **kwargs,
        )
        self.pack_propagate(False)

        self.sides = sides
        self.final_val = final_val
        self.raw_val = raw_val
        self.was_boosted = was_boosted

        self.canvas = ctk.CTkCanvas(
            self,
            width=56,
            height=56,
            bg="#313244",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

        self.curr_val = random.randint(1, self.sides)
        self.next_val = random.randint(1, self.sides)

        self.text_curr = self.canvas.create_text(
            28, 28, text=str(self.curr_val), fill="#a6adc8", font=(SMOOTH_FONT[0], 18, "bold")
        )
        self.text_next = self.canvas.create_text(
            28, -20, text=str(self.next_val), fill="#a6adc8", font=(SMOOTH_FONT[0], 18, "bold")
        )

        self.offset = 0.0

    def start_roll(self, duration=2.0, on_finish_callback=None):
        self.start_time = time.perf_counter()
        self.last_frame_time = self.start_time
        self.duration = duration
        self.on_finish_callback = on_finish_callback

        self.configure(border_color="#cba6f7")
        self._animate_step()

    def _animate_step(self):
        now = time.perf_counter()
        elapsed = now - self.start_time
        dt = now - self.last_frame_time
        self.last_frame_time = now

        if elapsed < self.duration:
            progress = elapsed / self.duration

            ease_factor = (1.0 - progress) ** 3.5
            pixels_per_second = 80.0 + (ease_factor * 1600.0)

            self.offset += pixels_per_second * dt

            while self.offset >= 48.0:
                self.offset -= 48.0
                self.curr_val = self.next_val

                if progress > 0.70:
                    self.next_val = self.final_val
                else:
                    self.next_val = random.randint(1, self.sides)

                self.canvas.itemconfig(self.text_curr, text=str(self.curr_val))
                self.canvas.itemconfig(self.text_next, text=str(self.next_val))

            y_curr = 28.0 + self.offset
            y_next = -20.0 + self.offset

            self.canvas.coords(self.text_curr, 28, y_curr)
            self.canvas.coords(self.text_next, 28, y_next)

            self.after(10, self._animate_step)
        else:
            self.canvas.coords(self.text_curr, 28, 28)
            self.canvas.coords(self.text_next, 28, -50)
            self.canvas.itemconfig(self.text_curr, text=str(self.final_val))

            half_value = self.sides / 2
            if self.final_val < half_value:
                res_color = "#f38ba8"
            else:
                res_color = "#a6e3a1"

            bg_color = "#45475a" if self.was_boosted else "#313244"

            self.canvas.itemconfig(self.text_curr, fill=res_color)
            self.canvas.configure(bg=bg_color)
            self.configure(border_color=res_color, fg_color=bg_color)

            if self.on_finish_callback:
                self.on_finish_callback()


class RPGDiceRoller(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("RPG Dice Roller")
        self.geometry("500x720")
        self.resizable(False, False)

        self.is_rolling = False
        self.current_dice_index = 0
        self.created_cards = []
        self.history_items = []

        self.history_visible = False

        # --- HEADER SECTION ---
        self.lbl_header = ctk.CTkLabel(
            self,
            text="🎲 RPG DICE ROLLER 🎲",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=22, weight="bold"),
            text_color="#cba6f7",
        )
        self.lbl_header.pack(pady=(15, 5))

        # --- INPUTS SECTION ---
        self.frame_inputs = ctk.CTkFrame(self, corner_radius=12)
        self.frame_inputs.pack(fill="x", padx=20, pady=10)
        self.frame_inputs.grid_columnconfigure(0, weight=1)
        self.frame_inputs.grid_columnconfigure(1, weight=0)

        # Dice Type
        ctk.CTkLabel(
            self.frame_inputs,
            text="Dice Type:",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.dice_type = ctk.StringVar(value="d20")
        dice_options = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]

        self.combo_dice = ctk.CTkOptionMenu(
            self.frame_inputs,
            values=dice_options,
            variable=self.dice_type,
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13),
            width=120,
            fg_color="#cba6f7",
            button_color="#b4befe",
            button_hover_color="#cba6f7",
            text_color="#11111b",
        )
        self.combo_dice.grid(row=0, column=1, padx=15, pady=8, sticky="e")

        # Dice Count (Max 6)
        ctk.CTkLabel(
            self.frame_inputs,
            text="Dice Count (1-6):",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13, weight="bold")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="w")

        self.spin_count = ctk.CTkEntry(
            self.frame_inputs,
            width=120,
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13),
            placeholder_text="1"
        )
        self.spin_count.insert(0, "1")
        self.spin_count.grid(row=1, column=1, padx=15, pady=8, sticky="e")

        # Minimum Value
        ctk.CTkLabel(
            self.frame_inputs,
            text="Min Value per Die:",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13, weight="bold"),
        ).grid(row=2, column=0, padx=15, pady=8, sticky="w")

        self.spin_min_val = ctk.CTkEntry(
            self.frame_inputs,
            width=120,
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13),
            placeholder_text="1"
        )
        self.spin_min_val.insert(0, "1")
        self.spin_min_val.grid(row=2, column=1, padx=15, pady=8, sticky="e")

        # Modifier + Checkbox "Per Die"
        ctk.CTkLabel(
            self.frame_inputs,
            text="Modifier (+/-):",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13, weight="bold"),
        ).grid(row=3, column=0, padx=15, pady=8, sticky="w")

        self.mod_container = ctk.CTkFrame(self.frame_inputs, fg_color="transparent")
        self.mod_container.grid(row=3, column=1, padx=15, pady=8, sticky="e")

        self.chk_per_die = ctk.CTkCheckBox(
            self.mod_container,
            text="Per Die",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=11, weight="bold"),
            fg_color="#cba6f7",
            hover_color="#b4befe",
            checkmark_color="#11111b",
            border_color="#45475a",
            width=70,
            checkbox_width=18,
            checkbox_height=18,
        )
        self.chk_per_die.pack(side="left", padx=(0, 8))

        self.spin_modifier = ctk.CTkEntry(
            self.mod_container,
            width=65,
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13),
            placeholder_text="0"
        )
        self.spin_modifier.insert(0, "0")
        self.spin_modifier.pack(side="right")

        # --- ROLL BUTTON ---
        self.btn_roll = ctk.CTkButton(
            self,
            text="ROLL DICE!",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=15, weight="bold"),
            height=44,
            fg_color="#cba6f7",
            text_color="#11111b",
            hover_color="#b4befe",
            command=self.start_roll_sequence,
        )
        self.btn_roll.pack(fill="x", padx=20, pady=10)

        # --- RESULT SECTION ---
        self.frame_result = ctk.CTkFrame(
            self, corner_radius=12, fg_color="#181825"
        )
        self.frame_result.pack(fill="x", padx=20, pady=5)

        self.btn_reset_result = ctk.CTkButton(
            self.frame_result,
            text="↺",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=16, weight="bold"),
            width=28,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#313244",
            text_color="#a6adc8",
            command=self.reset_result_view,
        )
        self.btn_reset_result.place(relx=1.0, rely=0.0, x=-8, y=8, anchor="ne")

        self.lbl_total = ctk.CTkLabel(
            self.frame_result,
            text="-",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=42, weight="bold"),
            text_color="#cba6f7",
        )
        self.lbl_total.pack(pady=(10, 0))

        self.lbl_details = ctk.CTkLabel(
            self.frame_result,
            text="Set your parameters and click Roll",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=12, slant="italic"),
            text_color="#a6adc8",
        )
        self.lbl_details.pack(pady=(0, 5))

        self.dice_display_frame = ctk.CTkFrame(
            self.frame_result, fg_color="transparent", height=75
        )
        self.dice_display_frame.pack(fill="x", padx=10, pady=(5, 10))

        # --- ROLL HISTORY HEADER WITH TOGGLE & CLEAR BUTTONS ---
        self.frame_history_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_history_header.pack(fill="x", padx=20, pady=(10, 2))

        self.lbl_history_title = ctk.CTkLabel(
            self.frame_history_header,
            text="Roll History",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=13, weight="bold"),
            text_color="#cdd6f4",
        )
        self.lbl_history_title.pack(side="left")

        self.btn_toggle_history = ctk.CTkButton(
            self.frame_history_header,
            text="▶ Show",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=11),
            width=65,
            height=24,
            fg_color="#313244",
            hover_color="#45475a",
            text_color="#cdd6f4",
            command=self.toggle_history,
        )
        self.btn_toggle_history.pack(side="right", padx=(5, 0))

        self.btn_clear_history = ctk.CTkButton(
            self.frame_history_header,
            text="Clear",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=11),
            width=55,
            height=24,
            fg_color="#313244",
            hover_color="#f38ba8",
            text_color="#cdd6f4",
            command=self.clear_history,
        )
        self.btn_clear_history.pack(side="right")

        # --- COLORFUL ROLL HISTORY LIST ---
        self.history_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=12,
            fg_color="#181825",
        )

        # --- DETAILED ASCII CAT CONTAINER ---
        self.ascii_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color="#181825",
        )

        self.lbl_ascii = ctk.CTkLabel(
            self.ascii_frame,
            text=ASCII_CAT_DETAILED,
            font=ctk.CTkFont(family=MONO_FONT[0], size=12, weight="bold"),
            text_color="#f5e0dc",
            justify="center",
        )
        self.lbl_ascii.pack(expand=True, fill="both")

        self.ascii_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def reset_result_view(self):
        if self.is_rolling:
            return

        self.lbl_total.configure(text="-")
        self.lbl_details.configure(text="Set your parameters and click Roll")

        for widget in self.dice_display_frame.winfo_children():
            widget.destroy()

        self.created_cards = []

    def toggle_history(self):
        if self.history_visible:
            self.history_frame.pack_forget()
            self.ascii_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            self.btn_toggle_history.configure(text="▶ Show")
            self.history_visible = False
        else:
            self.ascii_frame.pack_forget()
            self.history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            self.btn_toggle_history.configure(text="▼ Hide")
            self.history_visible = True

    def clear_history(self):
        for item in self.history_items:
            item.destroy()
        self.history_items.clear()

    def start_roll_sequence(self):
        if self.is_rolling:
            return

        # Pobieranie wartości z pól z obsługą pustych wartości (domyślne liczby)
        raw_count = self.spin_count.get().strip()
        raw_min = self.spin_min_val.get().strip()
        raw_mod = self.spin_modifier.get().strip()

        try:
            count = int(raw_count) if raw_count != "" else 1
            min_val = int(raw_min) if raw_min != "" else 1
            modifier = int(raw_mod) if raw_mod != "" else 0
        except ValueError:
            self.lbl_details.configure(
                text="Error: Please enter valid integers!"
            )
            return

        dice_str = self.dice_type.get()
        sides = int(dice_str.replace("d", ""))

        if count < 1 or count > 6:
            self.lbl_details.configure(
                text="Error: Dice count must be between 1 and 6!"
            )
            return

        if min_val > sides or min_val < 1:
            self.lbl_details.configure(
                text=f"Error: Min value must be between 1 and {sides}!"
            )
            return

        self.is_rolling = True

        self.btn_roll.configure(
            text="ROLLING...",
            fg_color="#45475a",
            text_color="#f38ba8",
            hover_color="#45475a"
        )

        self.lbl_total.configure(text="...")
        self.lbl_details.configure(text="Rolling...")

        for widget in self.dice_display_frame.winfo_children():
            widget.destroy()

        self.created_cards = []
        self.current_dice_index = 0

        raw_rolls = [random.randint(1, sides) for _ in range(count)]
        final_rolls = [max(roll, min_val) for roll in raw_rolls]

        is_per_die = bool(self.chk_per_die.get())
        total_modifier = (modifier * count) if is_per_die else modifier

        self.current_total = sum(final_rolls) + total_modifier
        self.current_rolls = final_rolls
        self.current_modifier = modifier
        self.current_is_per_die = is_per_die
        self.current_min_val = min_val
        self.current_dice_str = dice_str
        self.current_count = count

        # Wyśrodkowana ramka pomocnicza dla kostek
        center_container = ctk.CTkFrame(self.dice_display_frame, fg_color="transparent")
        center_container.pack(expand=True)

        for i in range(count):
            was_boosted = raw_rolls[i] < min_val
            card = SmoothRollingDiceCard(
                center_container,
                sides=sides,
                final_val=final_rolls[i],
                raw_val=raw_rolls[i],
                was_boosted=was_boosted,
            )
            card.pack(side="left", padx=4, pady=5)
            self.created_cards.append(card)

        self.roll_next_dice()

    def roll_next_dice(self):
        if self.current_dice_index < len(self.created_cards):
            card = self.created_cards[self.current_dice_index]
            card.start_roll(
                duration=2.0,
                on_finish_callback=self.on_single_dice_finished,
            )
        else:
            self.finalize_entire_roll()

    def on_single_dice_finished(self):
        self.current_dice_index += 1
        self.after(80, self.roll_next_dice)

    def finalize_entire_roll(self):
        self.lbl_total.configure(text=str(self.current_total))

        mod_str = ""
        if self.current_modifier != 0:
            sign = "+" if self.current_modifier > 0 else "-"
            per_die_label = " /die" if self.current_is_per_die else ""
            mod_str = f" {sign} {abs(self.current_modifier)}{per_die_label}"

        min_info = (
            f" (min {self.current_min_val})" if self.current_min_val > 1 else ""
        )
        self.lbl_details.configure(
            text=f"Rolled {self.current_count}{self.current_dice_str}{min_info}{mod_str}"
        )

        timestamp = datetime.now().strftime("%H:%M:%S")
        rolls_breakdown = " + ".join(str(val) for val in self.current_rolls)

        card = ctk.CTkFrame(self.history_frame, fg_color="#313244", corner_radius=8)

        lbl_info = ctk.CTkLabel(
            card,
            text=f"[{timestamp}] {self.current_count}{self.current_dice_str}{min_info}",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=12, weight="bold"),
            text_color="#cba6f7",
            anchor="w",
        )
        lbl_info.pack(fill="x", padx=10, pady=(6, 2))

        row_frame = ctk.CTkFrame(card, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=(0, 6))

        lbl_rolls = ctk.CTkLabel(
            row_frame,
            text=f"🎲 {rolls_breakdown}",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=12),
            text_color="#cdd6f4",
        )
        lbl_rolls.pack(side="left")

        if self.current_modifier != 0:
            per_die_suffix = " /die" if self.current_is_per_die else ""
            mod_text = f" ({'+' if self.current_modifier > 0 else ''}{self.current_modifier}{per_die_suffix})"
            lbl_mod = ctk.CTkLabel(
                row_frame,
                text=mod_text,
                font=ctk.CTkFont(family=SMOOTH_FONT[0], size=12),
                text_color="#89b4fa",
            )
            lbl_mod.pack(side="left")

        lbl_total_res = ctk.CTkLabel(
            row_frame,
            text=f"= Total: {self.current_total}",
            font=ctk.CTkFont(family=SMOOTH_FONT[0], size=12, weight="bold"),
            text_color="#a6e3a1",
        )
        lbl_total_res.pack(side="right")

        self.history_items.insert(0, card)
        for item in self.history_items:
            item.pack_forget()
            item.pack(fill="x", pady=4, padx=2)

        self.is_rolling = False

        self.btn_roll.configure(
            text="ROLL DICE!",
            fg_color="#cba6f7",
            text_color="#11111b",
            hover_color="#b4befe"
        )


if __name__ == "__main__":
    app = RPGDiceRoller()
    app.mainloop()
