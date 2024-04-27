import numpy as np
import csv
import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def load_data(first_plot_data):
    global data1, data2, data_changed
    file_name = filedialog.askopenfilename()
    if not file_name:
        return

    with open(file_name, 'r') as file:
        file = csv.reader(file)
        data = []
        for row in file:
            data.append(row[0])
    data_changed = True
    if first_plot_data:
        data1 = np.array(data, dtype=float)
    else:
        data2 = np.array(data, dtype=float)

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
            result = np.convolve(data1, data2, mode='full')
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
