import csv
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def preview_load_popup(data):
    def close_popup():
        nonlocal delimiter, channel
        delimiter = delimiter_entry.get("1.0", tk.END).strip()
        try:
            channel = int(channel_entry.get("1.0", tk.END).strip())
        except ValueError:
            channel = 0
        popup.destroy()
        root.focus_set()

    popup = tk.Toplevel(root)
    popup.wm_title("Konfiguracja wczytywanych danych")
    popup.geometry("400x400")
    popup.resizable(False, False)
    popup.grid_rowconfigure(0, weight=1)
    popup.grid_rowconfigure(1, weight=1)
    popup.grid_rowconfigure(2, weight=1)
    popup.grid_rowconfigure(3, weight=1)
    popup.grid_rowconfigure(4, weight=1)
    popup.grid_rowconfigure(5, weight=1)
    popup.grid_rowconfigure(6, weight=1)
    popup.grid_rowconfigure(7, weight=1)
    popup.grid_rowconfigure(8, weight=1)
    popup.grid_rowconfigure(9, weight=1)
    popup.grid_rowconfigure(10, weight=1)
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_columnconfigure(1, weight=1)

    tk.Label(popup, text="Dane do wczytania:").grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    for i in range(5):
        row = next(data)
        tk.Label(popup, text=row).grid(row=i+1, column=0, columnspan=2, padx=10, pady=2)

    tk.Label(popup, text="...").grid(row=6, column=0, columnspan=2, padx=10, pady=2)

    ttk.Separator(popup, orient=tk.HORIZONTAL, style='TSeparator').grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    tk.Label(popup, text="Znak podziału danych w wierszu:").grid(row=8, column=0, padx=10, pady=10)
    delimiter = ";"
    delimiter_entry = tk.Text(popup, height=1, width=5)
    delimiter_entry.insert(tk.END, delimiter)
    delimiter_entry.grid(row=8, column=1, padx=10, pady=10)
    
    tk.Label(popup, text="Wybrany kanał sygnału:").grid(row=9, column=0, padx=10, pady=10)
    channel = "0"
    channel_entry = tk.Text(popup, height=1, width=5)
    channel_entry.insert(tk.END, channel)
    channel_entry.grid(row=9, column=1, padx=10, pady=10)

    tk.Button(popup, text="Potwierdź", command=close_popup).grid(row=10, column=0, columnspan=2, padx=10, pady=10)

    root.wait_window(popup)
    return delimiter, channel

def load_data(first_plot_data):
    global data1, data2, data_changed
    file_name = filedialog.askopenfilename()
    if not file_name:
        return
    
    delimiter = ';'
    channel = 0
    with open(file_name, 'r') as file:
        loaded_data = csv.reader(file)
        delimiter, channel = preview_load_popup(loaded_data)

    with open(file_name, 'r') as file:
        loaded_data = csv.reader(file, delimiter=delimiter)
        data = []
        for row in loaded_data:
            data.append(float(row[channel]))
    data_changed = True
    if first_plot_data:
        data1 = data
    else:
        data2 = data

def save_data():
    global result
    file = filedialog.asksaveasfile(initialfile="result.csv", defaultextension=".csv")
    if not file:
        return
    writer = csv.writer(file)
    for row in result:
         writer.writerow([row])
    file.close()

def config_window():
    global result
    root = tk.Tk()
    root.wm_title("Splot dwóch sygnałów")
    root.geometry("800x600")
    root.protocol("WM_DELETE_WINDOW", quit)

    frame = tk.Frame(root)
    frame.pack(side="top", expand=True, fill="both")

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar)
    menu_bar.add_cascade(label="Dane", menu=file_menu)
    file_menu.add_command(label="Załaduj sygnał 1", command= lambda: load_data(True))
    file_menu.add_command(label="Załaduj sygnał 2", command= lambda: load_data(False))
    file_menu.add_separator()
    file_menu.add_command(label="Zapisz wynik", command=save_data, state='disabled')

    return root, frame, file_menu

def plot_data(fig):
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def prepare_plot(data1, data2, result):
    fig, ax = plt.subplots(3)
    ax[0].plot(data1, 'r')
    ax[0].set_title('Sygnał 1')
    ax[0].set_ylabel('Amplituda')
    ax[0].set_xlabel('Czas [s]')
    ax[1].plot(data2, 'g')
    ax[1].set_title('Sygnał 2')
    ax[1].set_ylabel('Amplituda')
    ax[1].set_xlabel('Czas [s]')
    ax[2].plot(result, 'b')
    ax[2].set_title('Wynik splotu')
    ax[2].set_ylabel('Amplituda')
    ax[2].set_xlabel('Czas [s]')
    fig.suptitle('Splot dwóch sygnałów')
    plt.tight_layout()
    return fig

def quit():
    global root, last_loop
    if last_loop:
        root.after_cancel(last_loop)
    root.quit()
    root.destroy()
    
def convolution(data1, data2):
    result = []
    for i in range(len(data1) + len(data2) - 1):
        value = 0
        for j in range(len(data1)):
            if i - j >= 0 and i - j < len(data2):
                value += data1[j] * data2[i - j]
        result.append(value)
    return result

def logic_loop():
    global data1, data2, result, data_changed, data_loaded, last_loop
    if data_changed:
        data_changed = False
        if not data_loaded:
            starter_frame.destroy()
        data_loaded = True
        for widget in frame.winfo_children():
            widget.destroy()
        if len(data1) and len(data2):
            file_menu.entryconfig("Zapisz wynik", state='active')
            result = convolution(data1, data2)
        fig = prepare_plot(data1, data2, result)
        plot_data(fig)
    last_loop = root.after(100, logic_loop)

if __name__ == "__main__":
    data1 = []
    data2 = []
    result = []
    data_changed = False
    data_loaded = False
    last_loop = None

    root, frame, file_menu = config_window()
    starter_frame = tk.Frame(root)
    starter_frame.pack(side="top", expand=True, fill="both")
    tk.Label(starter_frame, text="Aby rozpocząć, załaduj pliki z danymi w zakładce 'Dane'").pack()

    logic_loop()
    tk.mainloop()
