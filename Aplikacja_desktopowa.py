import tkinter as tk
from tkinter import messagebox
import serial
import time
import threading
import time
from datetime import datetime, timedelta

ser = None
data_previous = ''
save_data = 0

def connect_with_USART():
    selected_port = port_var.get()
    global ser

    try:
        ser = serial.Serial(selected_port, 9600, timeout=0)#polaczenie z portem
        time.sleep(2)
        if ser.is_open:
            connect_with_USART_button.config(text="Rozłącz", command=disconnect_with_USART)
            receive_button.config(state="normal")
            messagebox.showinfo("Sukces", f"Połączono się z portem " + selected_port)
            data_previous = ''

    except serial.SerialException as e:
        messagebox.showerror("Błąd", f"Nie można otworzyć portu: {e}")

def disconnect_with_USART():
    if ser.is_open:
        ser.close()
        connect_with_USART_button.config(text="Połącz", command=connect_with_USART)
        save_button.config(state="disabled")
        stop_saving_data()
        save_button.config(state="disabled")
        receive_button.config(state="disabled")
        messagebox.showinfo("Sukces", f"Rozłączono się z portem szeregowym")
        received_text.config(state=tk.NORMAL)  # właczenie edycji
        received_text.insert(tk.END, f"\n\n\n")
        received_text.config(state=tk.DISABLED)  # wyłączenie edycji
        received_text.see(tk.END)  # przewijanie
        text1.insert("1.0", f"\n\n\n")
        text2.insert("1.0", f"\n\n\n")

def send_temperature():
    temperature = entry.get()

    if not temperature.isdigit() or len(temperature) != 2:
        messagebox.showerror("Błąd", "Wprowadź wartość temperatury w zakresie od 12°C do 84°C.")
        return

    ser.write(temperature.encode())

def receive_data():
    global data_previous

    try:
        if ser and ser.is_open:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8')
                for i in range(len(data)):
                    if data[i] == 'A':
                        if save_data == 1:
                            temp_to_file(data_previous)
                        display_received_data(data_previous)
                        text_labels(data_previous)
                        data_previous = data[i]
                    else:
                        data_previous = data_previous + data[i]
    except Exception as e: #gdy nie ma połączenia z portem szeregowym
        ser.close()
        connect_with_USART_button.config(text="Połącz", command=connect_with_USART)
        messagebox.showerror("Błąd", f"Utracono połączenie z portem szeregowym")
        save_button.pack_forget()
        received_text.config(state=tk.NORMAL)  # właczenie edycji
        received_text.insert(tk.END, f"\n\n\n")
        received_text.config(state=tk.DISABLED)  # wyłączenie edycji
        received_text.see(tk.END)  # przewijanie

    root.after(100, receive_data)


def display_received_data(data):
    received_text.config(state=tk.NORMAL)  #właczenie edycji
    received_text.insert(tk.END, f"{data}\n")
    received_text.config(state=tk.DISABLED)  #wyłączenie edycji
    received_text.see(tk.END)  #przewijanie


def start_receiving_data():
    root.after(100, receive_data) #co 100ms ta funkcja sie uruchomi
    save_button.config(state="normal")


def saving_data():
    global save_data
    save_data = 1
    save_button.config(text="Zakończ zapis danych", command=stop_saving_data)

def stop_saving_data():
    global save_data
    save_data = 0
    save_button.config(text="Rozpocznij zapis danych", command=saving_data)

def temp_to_file(data):
    licznik = 0
    actual_temp = 0
    set_temp = 0
    asd = 0

    for i in range(len(data)):
        if data[i].isdigit():
            if licznik < 2:
                actual_temp = actual_temp * 10 + int(data[i])
            elif licznik >= 2 and licznik < 4:
                set_temp = set_temp * 10 + int(data[i])
            licznik += 1

    try:
        with open("Logi_wartosci.txt", 'a') as file:
            file.write(f"Temperatura rzeczywista: {actual_temp} C Temperatura zadana: {set_temp} C\n")

    except Exception as e:
        print(f"Podczas zapisu wystąpił błąd: {e}")

def text_labels(data):
    licznik = 0
    actual_temp = 0
    set_temp = 0

    for i in range(len(data)):
        if data[i].isdigit():
            if licznik < 2:
                actual_temp = actual_temp * 10 + int(data[i])
            elif licznik >= 2 and licznik < 4:
                set_temp = set_temp * 10 + int(data[i])
            licznik += 1

    text1.insert("1.0", str(actual_temp) + "°C")
    text2.insert("1.0", str(set_temp) + "°C")

root = tk.Tk() #utworzenie okinka
root.title("Aplikacja do przesyłania i odbierania danych")

label = tk.Label(root, text="Wprowadź wartość temperatury w zakresie od 12°C do 84°C:")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

send_button = tk.Button(root, text="Wyślij", command=send_temperature)
send_button.pack(pady=10)

port_label = tk.Label(root, text="Wybierz port szeregowy:")
port_label.pack(pady=10)

port_var = tk.StringVar(root)
port_var.set("COM4")

ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
port_menu = tk.OptionMenu(root, port_var, *ports)
port_menu.pack(pady=5)

connect_with_USART_button = tk.Button(root, text="Połącz", command=connect_with_USART)
connect_with_USART_button.pack(pady=10)

received_text = tk.Text(root, height=3, state=tk.DISABLED)
received_text.pack(pady=10)

receive_button = tk.Button(root, text="Odbieraj dane", command=start_receiving_data)
receive_button.pack(pady=10)
receive_button.config(state="disabled")

save_button = tk.Button(root, text="Rozpocznij zapis danych", command=saving_data)
save_button.pack(pady=10)
save_button.config(state="disabled")

# Ramka 1 dla pierwszego pola tekstowego i etykiety
frame1 = tk.Frame(root)
frame1.pack(side=tk.LEFT, padx=10, pady=10)

label_text1 = tk.Label(frame1, text="Aktualna temperatura:", font=("Helvetica", 25))
label_text1.pack(pady=5)

text1 = tk.Text(frame1, height=1, width=4, font=("Helvetica", 75))
text1.pack(padx=5)

frame2 = tk.Frame(root)
frame2.pack(side=tk.LEFT, padx=10, pady=10)

label_text2 = tk.Label(frame2, text="Temperatura zadana:", font=("Helvetica", 25))
label_text2.pack(pady=5)

text2 = tk.Text(frame2, height=1, width=4, font=("Helvetica", 75))
text2.pack(padx=5)

root.mainloop()
