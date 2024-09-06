import serial
import time
import threading
import random
from datetime import datetime

# Konfiguracja portu szeregowego (zmień parametry według swoich potrzeb)
ser = serial.Serial(
    port='COM6',
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0
)

# Pobranie okresu wysyłania od użytkownika
while True:
    try:
        okres_wysylania = int(input("Co ile milisekund wysyłać wiadomość? (wpisz 'exit' aby zakończyć): "))
        if okres_wysylania <= 0:
            print("Okres wysyłania musi być liczbą dodatnią.")
        else:
            break
    except ValueError:
        if input().lower() == 'exit':
            print("Zakończono program.")
            exit()
        else:
            print("Nieprawidłowy format. Podaj liczbę całkowitą.")

# Pobranie czasu trwania wysyłania wiadomości
while True:
    try:
        czas_trwania = int(input("Jak długo (w sekundach) wysyłać wiadomości? (wpisz 'exit' aby zakończyć): "))
        if czas_trwania <= 0:
            print("Czas trwania musi być liczbą dodatnią.")
        else:
            break
    except ValueError:
        if input().lower() == 'exit':
            print("Zakończono program.")
            exit()
        else:
            print("Nieprawidłowy format. Podaj liczbę całkowitą.")

# Utworzenie pliku do zapisywania danych
log_file_path = "random_numbers_log.txt"

def zapis_danych(losowy_argument):
    """Funkcja zapisująca losowy argument i znacznik czasu do pliku."""
    with open(log_file_path, 'a') as file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - {losowy_argument}\n")

def komunikacja_szeregowa():
    global ser
    start_time = time.time()
    while True:
        # Losowy czwarty argument (np. liczba całkowita w zakresie od 1 do 100)
        losowy_argument = random.randint(1, 100)
        
        # Składanie wiadomości
        wiadomosc = f"chat private 0x0001 {losowy_argument}\n"
        
        # Wysyłanie wiadomości
        ser.write(wiadomosc.encode('ascii'))

        # Zapisanie danych do pliku
        zapis_danych(losowy_argument)

        # Odczytywanie danych (np. 255 bajtów)
        try:
            odczytane_dane = ser.read(255).decode('ascii').strip()
            if odczytane_dane:
                print("Otrzymano dane:", odczytane_dane)
                # Tutaj możesz dodać swoje własne przetwarzanie danych
        except UnicodeDecodeError:
            print("Błąd dekodowania danych.")
        
        # Sprawdzenie, czy czas trwania wysyłania minął
        elapsed_time = time.time() - start_time
        if elapsed_time > czas_trwania:
            break

        time.sleep(okres_wysylania / 1000.0)

# Utworzenie wątku
wątek_komunikacji = threading.Thread(target=komunikacja_szeregowa)

# Uruchomienie wątku
wątek_komunikacji.start()

# Główna pętla programu (możesz tu dodać inne funkcjonalności)
while True:
    # Sprawdzenie, czy użytkownik wpisał "exit"
    if input("Wpisz 'exit' aby zakończyć: ") == 'exit':
        # Zakończ wątek (możesz użyć flagi, jeśli wątek wymaga)
        break

# Zakończenie programu
ser.close()
print("Program zakończony.")
