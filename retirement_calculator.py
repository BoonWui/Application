import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import re

class RetirementCalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Enhanced Retirement Calculator")
        root.geometry("750x700")  # Smaller height to start
        root.minsize(700, 600)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.default_font = ("Segoe UI", 10)  # Slightly smaller font
        self.var_savings = tk.StringVar()
        self.var_contrib = tk.StringVar()
        self.var_return = tk.StringVar()
        self.var_target = tk.StringVar()
        self.var_current_age = tk.StringVar()
        self.var_retire_age = tk.StringVar()
        self.var_inflation = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self.root, padding=10)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(3, weight=1)  # Make chart frame grow

        title = ttk.Label(container, text="Retirement Calculator", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, pady=(0, 8))

        input_frame = ttk.Frame(container)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10)
        input_frame.columnconfigure(0, minsize=190)
        input_frame.columnconfigure(1, weight=1)

        # Compact input rows with smaller padding
        def add_entry(label_text, var, row):
            label = ttk.Label(input_frame, text=label_text, font=self.default_font, anchor="w")
            label.grid(row=row, column=0, sticky='w', pady=3)
            entry = ttk.Entry(input_frame, textvariable=var, font=self.default_font)
            entry.grid(row=row, column=1, sticky='ew', padx=(5, 0), pady=3)
            return entry

        add_entry("Current Savings (RM):", self.var_savings, 0)
        add_entry("Annual Contribution (RM):", self.var_contrib, 1)
        add_entry("Expected Annual Return (%):", self.var_return, 2)
        add_entry("Target Retirement Amount (RM):", self.var_target, 3)
        add_entry("Current Age:", self.var_current_age, 4)
        add_entry("Expected Retirement Age:", self.var_retire_age, 5)
        add_entry("Expected Inflation Rate (%):", self.var_inflation, 6)

        for var in [self.var_savings, self.var_contrib, self.var_target]:
            var.trace_add('write', self.on_entry_change)

        self.calc_button = ttk.Button(container, text="Calculate and Show Chart", command=self.calculate_and_plot)
        self.calc_button.grid(row=2, column=0, pady=10, sticky='ew', padx=10)

        self.result_text = tk.Text(container, height=5, font=self.default_font, state='disabled', wrap='word')
        self.result_text.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.chart_frame = ttk.Frame(container)
        self.chart_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0,10))
        container.rowconfigure(4, weight=3)  # Give chart even more grow weight
        self.chart_frame.columnconfigure(0, weight=1)
        self.chart_frame.rowconfigure(0, weight=1)

    def on_entry_change(self, *args):
        for var in [self.var_savings, self.var_contrib, self.var_target]:
            value = var.get()
            if value == '':
                continue
            new_value = self.add_commas_to_number(value)
            if new_value != value:
                var.set(new_value)

    def add_commas_to_number(self, s):
        s = re.sub(r"[^\d.]", "", s)
        if s == '':
            return ''
        if s.count('.') > 1:
            return s[:-1]
        if '.' in s:
            integer_part, decimal_part = s.split('.', 1)
            integer_part = f"{int(integer_part):,}" if integer_part else '0'
            return integer_part + '.' + decimal_part
        else:
            return f"{int(s):,}"

    def format_currency(self, num):
        return f"{num:,.2f}"

    def validate_inputs(self):
        try:
            current_savings = float(self.var_savings.get().replace(',', ''))
            annual_contrib = float(self.var_contrib.get().replace(',', ''))
            annual_return = float(self.var_return.get()) / 100
            target = float(self.var_target.get().replace(',', ''))
            current_age = int(self.var_current_age.get())
            retire_age = int(self.var_retire_age.get())
            inflation = float(self.var_inflation.get()) / 100
            return current_savings, annual_contrib, annual_return, target, current_age, retire_age, inflation
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers in all fields.")
            return None

    def calculate_and_plot(self):
        vals = self.validate_inputs()
        if not vals:
            return
        current_savings, annual_contrib, annual_return, target, current_age, retire_age, inflation = vals

        years_until_retirement = retire_age - current_age
        if years_until_retirement <= 0:
            messagebox.showerror("Input Error", "Expected retirement age must be greater than current age.")
            return

        adjusted_target = target * ((1 + inflation) ** years_until_retirement)

        years = 0
        balance = current_savings
        balances = [balance]
        year_labels = [0]

        while balance < adjusted_target and years < 100:
            balance = balance * (1 + annual_return) + annual_contrib
            years += 1
            balances.append(balance)
            year_labels.append(years)

        if years <= years_until_retirement:
            status = "🟢 On Track"
        elif years <= years_until_retirement + 5:
            status = "🟡 Needs Improvement"
        else:
            status = "🔴 Off Track"

        if years >= 100:
            result_msg = "❌ Retirement goal not reached in 100 years."
        else:
            result_msg = (
                f"✅ You can retire in approximately {years} years.\n"
                f"Final savings: RM {self.format_currency(balance)}\n"
                f"Target (inflation-adjusted): RM {self.format_currency(adjusted_target)}\n"
                f"Retirement Readiness: {status}"
            )

        self.result_text.config(state='normal')
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result_msg)
        self.result_text.config(state='disabled')

        self.plot_chart(year_labels, balances, adjusted_target)

    def plot_chart(self, year_labels, balances, adjusted_target):
        plt.close('all')
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(year_labels, balances, marker='o', label='Your Savings')
        ax.axhline(y=adjusted_target, color='r', linestyle='--', label='Target')
        ax.set_title("Savings Over Time")
        ax.set_xlabel("Years")
        ax.set_ylabel("Total Savings (RM)")
        ax.legend()
        ax.grid(True)
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{int(x):,}"))

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = RetirementCalculatorApp(root)
    root.mainloop()
