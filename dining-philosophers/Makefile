# Makefile for the "Dining Philosophers" program

# Program name
TARGET = dining_philosophers

# Compiler and compilation flags
CXX = g++
CXXFLAGS = -std=c++11 -pthread

# Source files
SRC = dining_philosophers.cpp

# Default target (compiling the program)
all: $(TARGET)

# Rule to compile the program
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

# Target to run the program
run: $(TARGET)
	./$(TARGET)

# Target to clean object and output files
clean:
	rm -f $(TARGET)

# Target to run the program with a specified number of philosophers
run_with_args: $(TARGET)
	./$(TARGET) $(ARGS)

.PHONY: all run clean run_with_args
