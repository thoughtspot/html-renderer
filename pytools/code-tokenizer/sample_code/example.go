package main

import (
	"fmt"
	"os"
	"strings"
)

// Constants for greeting
const (
	DefaultName = "World"
	Greeting    = "Hello"
)

// greetUser prepares a greeting message.
// It takes a name and returns the formatted greeting string.
func greetUser(name string) string {
	if strings.TrimSpace(name) == "" {
		name = DefaultName // Use default if name is empty
	}
	return fmt.Sprintf("%s, %s!", Greeting, name)
}

func main() {
	// Get name from environment variable or use default
	userName := os.Getenv("USERNAME")
	if userName == "" {
		userName = DefaultName // Fallback if USERNAME is not set
	}

	// Get the greeting and print it
	message := greetUser(userName)
	fmt.Println(message) // Output: Hello, [Name]!

	// Simple calculation
	x := 5
	y := 7
	fmt.Printf("%d * %d = %d\n", x, y, x*y) // Output: 5 * 7 = 35
}
