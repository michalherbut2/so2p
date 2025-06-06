#include <iostream>
#include <thread>
#include <vector>
#include <random>
#include <mutex>

// Default number of philosophers
const int DEFAULT_NUM_PHILOSOPHERS = 5;

// Global mutex for printing messages
std::mutex global_lock;

// Function for safely printing messages
void safe_print(const std::string& message) {
    global_lock.lock();
    std::cout << message << std::endl;
    global_lock.unlock();
}

// Class representing a philosopher
class Philosopher {
private:
    int id;
    std::mutex *leftFork;
    std::mutex *rightFork;
    int mealsEaten;
    bool running;
    std::mt19937 rng;
    std::uniform_int_distribution<int> timeDist;

public:
    Philosopher(int id, std::mutex *left, std::mutex *right)
        : id(id), leftFork(left), rightFork(right),
          mealsEaten(0), running(true),
          rng(id * 1000 + 42), // Unique seed 
          timeDist(1, 4) {}

    void run() {
        while (running) {

            // For the last philosopher, reverse the order to avoid deadlock
            if (id == DEFAULT_NUM_PHILOSOPHERS - 1) {
              std::swap(leftFork, rightFork);
            }

            // safe_print("[Philosopher " + std::to_string(id) + "] trying to pick up fork");
            leftFork->lock();
            // safe_print("[Philosopher " + std::to_string(id) + "] picked up fork");

            // safe_print("[Philosopher " + std::to_string(id) + "] trying to pick up second fork");
            rightFork->lock();
            // safe_print("[Philosopher " + std::to_string(id) + "] picked up second fork");

            eat();

            rightFork->unlock();
            // safe_print("[Philosopher " + std::to_string(id) + "] put down second fork");

            leftFork->unlock();
            // safe_print("[Philosopher " + std::to_string(id) + "] put down first fork");

            think();
        }
    }

    void stop() {
        running = false;
    }

    int getMealsEaten() const {
        return mealsEaten;
    }

private:
    void think() {
        safe_print("[Philosopher " + std::to_string(id) + "] is thinking...");

        // Release the lock while thinking
        std::this_thread::sleep_for(std::chrono::seconds(timeDist(rng)) * 2);
    }

    void eat() {
        safe_print("[Philosopher " + std::to_string(id) + "] is eating...");
        
        // Release the lock while eating
        std::this_thread::sleep_for(std::chrono::seconds(timeDist(rng)));
        mealsEaten++;
    }
};

int main(int argc, char* argv[]) {
    int numPhilosophers = DEFAULT_NUM_PHILOSOPHERS;

    // Check if the number of philosophers is passed as an argument
    if (argc > 1) {
        try {
            numPhilosophers = std::stoi(argv[1]);
        } catch (const std::invalid_argument& e) {
            std::cerr << "Invalid argument: " << argv[1] << ". Using default number of philosophers." << std::endl;
        }
    }

    safe_print("=== THE DINING PHILOSOPHERS PROBLEM ===");
    safe_print("Solution method: resource hierarchy");

    // Initialize locks for forks
    std::vector<std::mutex> forks(numPhilosophers);

    // Initialize philosophers
    std::vector<Philosopher> philosophers;
    for (int i = 0; i < numPhilosophers; i++) {
        std::mutex* leftFork = &forks[i];
        std::mutex* rightFork = &forks[(i + 1) % numPhilosophers];
        philosophers.emplace_back(i, leftFork, rightFork);
    }

    // Start philosopher threads
    std::vector<std::thread> threads;
    for (int i = 0; i < numPhilosophers; i++) {
        threads.emplace_back(&Philosopher::run, &philosophers[i]);
    }

    // Run the program for 60 seconds
    std::this_thread::sleep_for(std::chrono::seconds(60));

    // Stop the philosophers
    for (auto& philosopher : philosophers) {
        philosopher.stop();
    }
    safe_print("Ending the simulation...");

    // Wait for threads to finish
    for (auto& thread : threads) {
        if (thread.joinable()) {
            thread.join();
        }
    }

    // Display meal statistics
    safe_print("\n=== MEAL STATISTICS ===");
    int totalMeals = 0;
    for (int i = 0; i < numPhilosophers; i++) {
        int meals = philosophers[i].getMealsEaten();
        totalMeals += meals;
        safe_print("Philosopher " + std::to_string(i) + " ate " + std::to_string(meals) + " meals");
    }
    safe_print("Total meals eaten: " + std::to_string(totalMeals) + " meals");
    safe_print("Average meals per philosopher: " + std::to_string(static_cast<float>(totalMeals) / numPhilosophers));

    return 0;
}
