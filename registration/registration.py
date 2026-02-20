import json
import os
import re


class User:
   
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email

    def to_dict(self):
        """
        stored in JSON file.
        """
        return {
            "name": self.name,
            "age": self.age,
            "email": self.email
        }


class RegistrationSystem:
    """
    Manages user registration, validation,
    duplicate checking and persistent storage.
    """

    def __init__(self, filename="users.json"):
        self.filename = filename
        self.users = []
        self.load_users()

    def load_users(self):
        """
        Loads existing users from file if present.
        If file does not exist, initializes empty list.
        """
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                try:
                    self.users = json.load(file)
                except json.JSONDecodeError:
                    self.users = []
        else:
            self.users = []

    def save_users(self):
        """
        Saves current users list into JSON file
        ensuring persistence across executions.
        """
        with open(self.filename, "w") as file:
            json.dump(self.users, file, indent=4)

    def is_valid_name(self, name):
        """
        Validates that name contains only alphabets
        and is not empty.
        """
        return name.isalpha() and len(name) > 0

    def is_valid_age(self, age):
        """
        Validates that age is numeric and between 1 and 120.
        """
        if not age.isdigit():
            return False
        age = int(age)
        return 1 <= age <= 120

    def is_valid_email(self, email):
        """
        Validates email using regular expression pattern.
        """
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    def is_duplicate_email(self, email):
        """
        Checks whether the given email already exists.
        """
        for user in self.users:
            if user["email"] == email:
                return True
        return False

    def register_user(self, name, age, email):
        """
        Registers a new user after performing
        all validations and duplicate checks.
        """
        if not self.is_valid_name(name):
            return "Invalid name. Only alphabets allowed."

        if not self.is_valid_age(age):
            return "Invalid age. Enter number between 1 and 120."

        if not self.is_valid_email(email):
            return "Invalid email format."

        if self.is_duplicate_email(email):
            return "Email already registered."

        new_user = User(name, int(age), email)
        self.users.append(new_user.to_dict())
        self.save_users()

        return "User registered successfully."

    def display_users(self):
        """
        Displays all registered users.
        """
        if not self.users:
            print("No users registered yet.")
            return

        for index, user in enumerate(self.users, start=1):
            print(f"{index}. Name: {user['name']}, Age: {user['age']}, Email: {user['email']}")


def main():
    """
    Entry point of the application.
    Provides simple command-line interface
    for interacting with the registration system.
    """

    system = RegistrationSystem()

    while True:
        print("\n1. Register User")
        print("2. View Users")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Enter name: ")
            age = input("Enter age: ")
            email = input("Enter email: ")

            result = system.register_user(name, age, email)
            print(result)

        elif choice == "2":
            system.display_users()

        elif choice == "3":
            print("Exiting system.")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
