import tkinter as tk
from tkinter import messagebox, ttk
from math import log, sqrt, exp
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def black76_price_and_greeks(F, K, T, r, sigma, option_type='call'):
    if T <= 0 or sigma <= 0 or F <= 0 or K <= 0:
        return 0.0, 0, 0, 0, 0, 0

    d1 = (log(F / K) + 0.5 * sigma ** 2 * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    discount_factor = exp(-r * T)
    pdf_d1 = norm.pdf(d1)

    if option_type == 'call':
        price = discount_factor * (F * norm.cdf(d1) - K * norm.cdf(d2))
        delta = discount_factor * norm.cdf(d1)
        theta = (-F * sigma * discount_factor * pdf_d1 / (2 * sqrt(T))
                 - r * K * discount_factor * norm.cdf(d2))
        rho = -T * K * discount_factor * norm.cdf(d2)
    else:  # put
        price = discount_factor * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
        delta = -discount_factor * norm.cdf(-d1)
        theta = (-F * sigma * discount_factor * pdf_d1 / (2 * sqrt(T))
                 + r * K * discount_factor * norm.cdf(-d2))
        rho = T * K * discount_factor * norm.cdf(-d2)

    gamma = discount_factor * pdf_d1 / (F * sigma * sqrt(T))
    vega = F * discount_factor * pdf_d1 * sqrt(T)

    return price, delta, gamma, vega, theta, rho

def calculate():
    try:
        global F, T, r, sigma, option_type, strike_range, prices, greeks_data

        F = float(entry_futures.get())
        K = float(entry_strike.get())
        T = float(entry_time.get()) / 365  # days to years
        r = float(entry_rate.get()) / 100
        sigma = float(entry_volatility.get()) / 100
        option_type = var_option.get()

        price, delta, gamma, vega, theta, rho = black76_price_and_greeks(F, K, T, r, sigma, option_type)

        label_result.config(text=(
            f"Option Price: RM {price:.4f}\n"
            f"Delta: {delta:.4f}\n"
            f"Gamma: {gamma:.6f}\n"
            f"Vega: {vega:.4f}\n"
            f"Theta: {theta:.4f}\n"
            f"Rho: {rho:.4f}"
        ))

        strike_range = [K * (0.8 + 0.4 * i/49) for i in range(50)]

        prices = []
        delta_list = []
        gamma_list = []
        vega_list = []
        theta_list = []
        rho_list = []

        for strike in strike_range:
            p, d, g, v, th, ro = black76_price_and_greeks(F, strike, T, r, sigma, option_type)
            prices.append(p)
            delta_list.append(d)
            gamma_list.append(g)
            vega_list.append(v)
            theta_list.append(th)
            rho_list.append(ro)

        greeks_data = {
            'Delta': delta_list,
            'Gamma': gamma_list,
            'Vega': vega_list,
            'Theta': theta_list,
            'Rho': rho_list
        }

        plot_graph("Option Price")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

def plot_graph(selection):
    for widget in chart_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(7, 5))  # slightly bigger figure

    if selection == "Option Price":
        ax.plot(strike_range, prices, label="Option Price", color='blue')
        ax.set_ylabel("Option Price (RM)")
    else:
        ax.plot(strike_range, greeks_data[selection], label=selection, color='green')
        ax.set_ylabel(selection)

    ax.set_xlabel("Strike Price (K)")
    ax.set_title(f"{selection} vs Strike Price")
    ax.grid(True)
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def on_graph_select(event):
    selection = combo_graph.get()
    plot_graph(selection)

app = tk.Tk()
app.title("Black Futures Option Calculator with Greeks (FCPO)")
app.geometry("620x720")  # increase height for bigger chart
app.resizable(False, False)

label_font = ("Segoe UI", 11)
entry_font = ("Segoe UI", 11)
result_font = ("Segoe UI", 12, "bold")

input_frame = tk.Frame(app, padx=15, pady=8)  # less pady for compactness
input_frame.pack(fill='x')

tk.Label(input_frame, text="Futures Price (F):", font=label_font).grid(row=0, column=0, sticky='e', pady=4, padx=5)
entry_futures = tk.Entry(input_frame, font=entry_font, width=20)
entry_futures.grid(row=0, column=1, pady=4, padx=5)

tk.Label(input_frame, text="Strike Price (K):", font=label_font).grid(row=1, column=0, sticky='e', pady=4, padx=5)
entry_strike = tk.Entry(input_frame, font=entry_font, width=20)
entry_strike.grid(row=1, column=1, pady=4, padx=5)

tk.Label(input_frame, text="Time to Expiry (days):", font=label_font).grid(row=2, column=0, sticky='e', pady=4, padx=5)
entry_time = tk.Entry(input_frame, font=entry_font, width=20)
entry_time.grid(row=2, column=1, pady=4, padx=5)

tk.Label(input_frame, text="Risk-free Rate (%):", font=label_font).grid(row=3, column=0, sticky='e', pady=4, padx=5)
entry_rate = tk.Entry(input_frame, font=entry_font, width=20)
entry_rate.grid(row=3, column=1, pady=4, padx=5)

tk.Label(input_frame, text="Volatility (%):", font=label_font).grid(row=4, column=0, sticky='e', pady=4, padx=5)
entry_volatility = tk.Entry(input_frame, font=entry_font, width=20)
entry_volatility.grid(row=4, column=1, pady=4, padx=5)

option_frame = tk.Frame(input_frame)
option_frame.grid(row=5, column=0, columnspan=2, pady=(8, 12))

var_option = tk.StringVar(value='call')
tk.Radiobutton(option_frame, text="Call Option", variable=var_option, value='call', font=label_font).pack(side='left', padx=15)
tk.Radiobutton(option_frame, text="Put Option", variable=var_option, value='put', font=label_font).pack(side='left', padx=15)

btn_calc = tk.Button(app, text="Calculate", font=("Segoe UI", 12, "bold"), command=calculate, bg="#4CAF50", fg="white", width=30, relief="raised")
btn_calc.pack(pady=(0, 6))

label_result = tk.Label(app, 
                        text="Option Price: RM 0.0000\nDelta: 0.0000\nGamma: 0.000000\nVega: 0.0000\nTheta: 0.0000\nRho: 0.0000",
                        font=result_font, justify="left", padx=15)
label_result.pack(pady=(0,6), anchor='w')

combo_frame = tk.Frame(app)
combo_frame.pack(fill='x', padx=15, pady=(0,6))

tk.Label(combo_frame, text="Select Graph:", font=label_font).pack(side='left', padx=(0,10))

combo_graph = ttk.Combobox(combo_frame, values=["Option Price", "Delta", "Gamma", "Vega", "Theta", "Rho"], state="readonly", font=label_font, width=15)
combo_graph.current(0)
combo_graph.pack(side='left')
combo_graph.bind("<<ComboboxSelected>>", on_graph_select)

chart_frame = tk.Frame(app, relief='sunken', borderwidth=1)
chart_frame.pack(fill='both', expand=True, padx=15, pady=(0,15))

app.mainloop()
