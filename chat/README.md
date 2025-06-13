# Chat Server - Wielowątkowy serwer czatu

## Opis problemu

Projekt implementuje wielowątkowy serwer czatu z obsługą wielu klientów jednocześnie. System składa się z dwóch głównych komponentów:

- **Serwer** (`server.py`) - centralna aplikacja obsługująca połączenia klientów i przekazująca wiadomości
- **Klient** (`client.py`) - aplikacja kliencka umożliwiająca użytkownikom dołączenie do czatu

Główne wyzwania synchronizacyjne obejmują:
- Bezpieczne zarządzanie listą aktywnych klientów
- Synchronizację dostępu do kolejki wiadomości
- Koordinację wyjścia z konsoli między wątkami
- Graceful shutdown wszystkich komponentów

## Instrukcje uruchomienia

### Wymagania
- Python 3.6 lub wyższy
- Biblioteki standardowe: `socket`, `threading`, `signal`

### Uruchomienie serwera
```bash
python server.py
```
Serwer uruchomi się na `127.0.0.1:8888` i będzie oczekiwał na połączenia klientów.

### Uruchomienie klienta
```bash
python client.py
```
Po uruchomieniu klient:
1. Połączy się z serwerem
2. Poprosi o podanie nazwy użytkownika
3. Umożliwi wysyłanie i odbieranie wiadomości

### Zamykanie aplikacji
- **Ctrl+C** - graceful shutdown zarówno serwera jak i klienta
- Serwer automatycznie rozłączy wszystkich klientów przy zamykaniu

## Wątki i co reprezentują

### Serwer (`server.py`)

1. **Wątek główny (Main Thread)**
   - Nasłuchuje na nowe połączenia klientów
   - Tworzy nowe wątki dla każdego klienta
   - Obsługuje sygnały zamykania (SIGINT)

2. **Wątki obsługi klientów (`handle_client`)**
   - Jeden wątek na każdego połączonego klienta
   - Odbiera wiadomości od konkretnego klienta
   - Dodaje wiadomości do kolejki do rozesłania
   - Zarządza lifecycle'em połączenia klienta

3. **Wątek przetwarzania wiadomości (`process_messages`)**
   - Pobiera wiadomości z kolejki
   - Rozesyła wiadomości do wszystkich klientów (broadcast)
   - Działa w pętli ciągłej aż do zamknięcia serwera

### Klient (`client.py`)

1. **Wątek główny (Main Thread)**
   - Nawiązuje połączenie z serwerem
   - Wysyła wiadomości wprowadzone przez użytkownika
   - Obsługuje sygnały zamykania

2. **Wątek odbierania wiadomości (`receive_messages`)**
   - Nasłuchuje na wiadomości przychodzące z serwera
   - Wyświetla otrzymane wiadomości w konsoli
   - Kończy działanie przy rozłączeniu

## Sekcje krytyczne i ich rozwiązanie

### 1. Zarządzanie listą klientów (`clients_mutex`)
**Problem:** Wielowątkowy dostęp do listy aktywnych klientów podczas dodawania, usuwania i iteracji.

**Rozwiązanie:**
```python
clients_mutex = threading.Lock()
```
- Synchronizuje operacje: `add_client()`, `remove_client()`, `broadcast_message()`
- Zapewnia atomowość operacji na strukturach danych klientów
- Chroni przed race conditions przy jednoczesnym dodawaniu/usuwaniu klientów

### 2. Kolejka wiadomości (`MessageQueue`)
**Problem:** Bezpieczne przekazywanie wiadomości między wątkami obsługi klientów a wątkiem broadcast'u.

**Rozwiązanie:**
```python
class MessageQueue:
    def __init__(self):
        self.queue_mutex = threading.Lock()
        self.not_empty = threading.Condition(self.queue_mutex)
```
- Implementuje thread-safe kolejkę z wykorzystaniem `Condition` variable
- `enqueue()` - bezpiecznie dodaje wiadomości i powiadamia wątek odbiorczy
- `dequeue()` - blokuje wątek do momentu pojawienia się wiadomości
- Timeout w `wait(0.1)` umożliwia graceful shutdown

### 3. Synchronizacja wyjścia konsoli (`print_mutex`)
**Problem:** Wielowątkowe wypisywanie do konsoli powoduje mieszanie się komunikatów.

**Rozwiązanie:**
```python
print_mutex = threading.Lock()

with print_mutex:
    print(message, end='')
```
- Zapewnia atomowość operacji wypisywania
- Stosowane zarówno w serwerze jak i kliencie
- Chroni przed przeplataaniem się komunikatów z różnych wątków