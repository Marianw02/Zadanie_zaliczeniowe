import tkinter as tk
from tkinter import messagebox
import serial
import time
import threading

ser = None
data_previous = ''

def connect_with_USART():
    selected_port = port_var.get()
    global ser

    try:
        ser = serial.Serial(selected_port, 9600, timeout=0)#polaczenie z portem
        time.sleep(2)
        if ser.is_open:
            connect_with_USART_button.config(text="Rozłącz", command=disconnect_with_USART)
            messagebox.showinfo("Sukces", f"Połączono się z portem " + selected_port)
            data_previous = ''

    except serial.SerialException as e:
        messagebox.showerror("Błąd", f"Nie można otworzyć portu: {e}")

def disconnect_with_USART():
    if ser.is_open:
        ser.close()
        connect_with_USART_button.config(text="Połącz", command=connect_with_USART)
        messagebox.showinfo("Sukces", f"Rozłączono się z portem szeregowym")

def send_temperature():
    temperature = entry.get()

    if not temperature.isdigit() or len(temperature) != 2:
        messagebox.showerror("Błąd", "Wprowadź wartość temperatury w zakresie od 12°C do 41°C.")
        return

    ser.write(temperature.encode())

def receive_data():
    global data_previous

    if ser and ser.is_open:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8')
            for i in range(len(data)):
                if data[i] == 'A':
                    display_received_data(data_previous)
                    data_previous = data[i]
                else:
                    data_previous = data_previous + data[i]

    root.after(100, receive_data)


def display_received_data(data):
    received_text.config(state=tk.NORMAL)  #właczenie edycji
    received_text.insert(tk.END, f"{data}\n")
    received_text.config(state=tk.DISABLED)  #wyłączenie edycji
    received_text.see(tk.END)  #przewijanie


def start_receiving_data():
    root.after(100, receive_data) #co 100ms ta funkcja sie uruchomi


def close_serial_connection():
    if ser and ser.is_open:
        ser.close()

root = tk.Tk() #utworzenie okinka
root.title("Aplikacja do przesyłania i odbierania danych")

label = tk.Label(root, text="Wprowadź wartość temperatury w zakresie od 12°C do 41°C:")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

send_button = tk.Button(root, text="Wyślij", command=send_temperature)
send_button.pack(pady=10)

port_label = tk.Label(root, text="Wybierz port szeregowy:")
port_label.pack(pady=10)

port_var = tk.StringVar(root)
port_var.set("COM1")

ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
port_menu = tk.OptionMenu(root, port_var, *ports)
port_menu.pack(pady=5)

connect_with_USART_button = tk.Button(root, text="Połącz", command=connect_with_USART)
connect_with_USART_button.pack(pady=10)

received_text = tk.Text(root, height=10, state=tk.DISABLED)
received_text.pack(pady=10)

receive_button = tk.Button(root, text="Odbieraj dane", command=start_receiving_data)
receive_button.pack(pady=10)

# Zamykanie połączenia szeregowego przed zamknięciem aplikacji
root.protocol("WM_DELETE_WINDOW", close_serial_connection)

# Uruchomienie aplikacji
root.mainloop()
