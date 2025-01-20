import tkinter as tk
from tkinter import messagebox
import serial
import time
import threading

ser = None


def send_temperature():
    temperature = entry.get()
    selected_port = port_var.get()

    if not temperature.isdigit() or len(temperature) != 2:
        messagebox.showerror("Błąd", "Wprowadź dwucyfrową liczbę.")
        return

    try:
        global ser
        if ser is None or not ser.is_open:
            ser = serial.Serial(selected_port, 9600, timeout=1)
            time.sleep(2)

        ser.write(temperature.encode())
        messagebox.showinfo("Sukces", f"Wysłano temperaturę: {temperature}°C do {selected_port}")

    except serial.SerialException as e:
        messagebox.showerror("Błąd", f"Nie można otworzyć portu: {e}")


def receive_data():
    if ser and ser.is_open:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            display_received_data(data)

    root.after(100, receive_data)


def display_received_data(data):
    received_text.config(state=tk.NORMAL)
    received_text.insert(tk.END, f"Odebrano: {data}\n")
    received_text.config(state=tk.DISABLED)
    received_text.see(tk.END)


def start_receiving_data():
    root.after(100, receive_data)


def close_serial_connection():
    if ser and ser.is_open:
        ser.close()


root = tk.Tk()
root.title("Aplikacja do przesyłania i odbierania danych")

label = tk.Label(root, text="Wprowadź dwucyfrową temperaturę (°C):")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

port_label = tk.Label(root, text="Wybierz port szeregowy:")
port_label.pack(pady=10)

port_var = tk.StringVar(root)
port_var.set("COM1")

ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
port_menu = tk.OptionMenu(root, port_var, *ports)
port_menu.pack(pady=5)

send_button = tk.Button(root, text="Wyślij", command=send_temperature)
send_button.pack(pady=10)

received_text = tk.Text(root, height=10, state=tk.DISABLED)
received_text.pack(pady=10)

receive_button = tk.Button(root, text="Odbieraj dane", command=start_receiving_data)
receive_button.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", close_serial_connection)

root.mainloop()
