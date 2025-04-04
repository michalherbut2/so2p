# Problem ucztujących filozofów (dining philosophers problem)

## Opis problemu

Problem ucztujących się filozofów jest klasycznym problemem synchronizacji i zarządzania współbieżnością. Opisuje sytuację, w której filozofowie siedzą przy okrągłym stole, każdy z nich ma talerz z jedzeniem i dwa widelce, które są dzielone z sąsiadami. Filozofowie naprzemiennie myślą i jedzą. Aby zjeść, filozof musi podnieść dwa widelce, jeden z lewej strony i jeden z prawej, a po zjedzeniu odłożyć je z powrotem na stół. Problem polega na tym, aby unikać zakleszczeń (deadlock), zjawiska, w którym filozofowie czekają na siebie nawzajem, oraz zagwarantować sprawiedliwy dostęp do widelców.

## Wątek i synchronizacja

Program implementuje klasyczny problem ucztujących się filozofów, gdzie każdy filozof jest reprezentowany przez oddzielny wątek. Filozofowie używają zamków (locks) do synchronizacji dostępu do widelców i uniknięcia zakleszczenia. Program wykorzystuje własną implementację zamka (`MyLock`), który jest używany do blokowania i odblokowywania widelców oraz do zapewnienia bezpieczeństwa dostępu do wspólnych zasobów.

## Instrukcje uruchomienia

### Wymagania
- C++11 lub wyższy
- Kompilator C++ obsługujący wątki (np. GCC, Clang, MSVC)

1. **Kopiowanie repozytorium:**
  ```bash
  git clone https://github.com/michalherbut2/so2p.git
  cd so2p/dining-philosophers
  ```

2. **Kompilacja programu:**
   Aby skompilować program, wystarczy użyć `Makefile`. Użyj poniższej komendy, aby skompilować program:
   ```bash
   make```

2. **Uruchomienie programu: Aby uruchomić program z domyślną liczbą filozofów (5), użyj:**

```bash
make run
```
2. **Uruchomienie programu z określoną liczbą filozofów (np. 7): Aby uruchomić program z określoną liczbą filozofów, podaj liczbę filozofów w argumencie:**

```bash
make run_with_args ARGS=7
```
2. **Czyszczenie plików: Aby usunąć pliki wynikowe (np. plik wykonywalny), użyj komendy:**

```bash
make clean
```

## Wątek i co reprezentują

Program składa się z następujących wątków:

- **Filozofowie (Philosopher):** Każdy filozof jest reprezentowany przez oddzielny wątek. Filozofowie naprzemiennie myślą i jedzą. Aby zjeść, filozofowie muszą podnieść dwa widelce — jeden z lewej i jeden z prawej strony. Wątek filozofa wykonuje metodę `run()`, która najpierw próbuje podnieść dwa widelce (przez zamek), a potem jeść, przełączając się między myśleniem i jedzeniem. 

## Sekcje krytyczne i ich rozwiązanie

Sekcje krytyczne to obszary, w których filozofowie próbują uzyskać dostęp do wspólnych zasobów — w tym przypadku do widelców. W celu zapewnienia poprawnej synchronizacji oraz uniknięcia zakleszczenia (deadlock), zastosowane zostały następujące rozwiązania:

- **Zamek na widelcu:** Każdy widelec jest reprezentowany przez obiekt klasy `MyLock`, który implementuje mechanizm blokady. Dzięki temu tylko jeden filozof może podnieść dany widelec w tym samym czasie. Działanie tego zamka bazuje na algorytmie blokującym z próbnym podejściem (busy-waiting), który w pętli sprawdza, czy widelec jest dostępny, a następnie blokuje dostęp do niego, aż zostanie zwolniony. Dodatkowo, zastosowano opóźnienie (`std::this_thread::sleep_for`), aby zminimalizować obciążenie procesora, kiedy filozofowie czekają na dostęp do widelca.

- **Hierarchia widelców:** Aby uniknąć zakleszczenia, filozofowie zawsze najpierw podnoszą widelec o niższym id, a potem ten o wyższym. Po zjedzeniu, zwracają je w odwrotnej kolejności: najpierw oddają widelec o wyższym id, a potem o niższym. W przypadku, gdy czterech filozofów jednocześnie podniesie widelce o niższym id, na stole pozostanie tylko jeden widelec — ten o najwyższym id. Piąty filozof nie będzie mógł podnieść żadnego widelca, ponieważ tylko jeden filozof ma dostęp do tego widelca. Kiedy ten filozof skończy jeść, odda widelce w odwrotnej kolejności, umożliwiając pozostałym filozofom zabranie ich i kontynuowanie jedzenia..

- **Zamek globalny:** Aby zapewnić, że komunikaty wypisywane przez filozofów do konsoli są bezpieczne, używamy globalnego zamka (`global_lock`). Synchronizuje on dostęp do konsoli, dzięki czemu zapobiega sytuacjom, w których różne wątki próbują jednocześnie wypisać swoje komunikaty, co mogłoby skutkować zniekształceniem wyników lub błędami w wyświetlaniu.
