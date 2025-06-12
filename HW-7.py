from datetime import datetime, timedelta
import re

# Декоратор для обробки помилок
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid number of arguments. Please provide the correct number of arguments."
        except KeyError:
            return "Contact not found."
    return inner

# Базовий клас Field
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для імені
class Name(Field):
    pass

# Клас для телефону з валідацією
class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate_phone(phone):
        return bool(re.match(r'^\d{10}$', phone))

# Клас для дня народження з валідацією (зберігає рядок)
class Birthday(Field):
    def __init__(self, value):
        if not self.validate_date(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)  # Зберігаємо значення як рядок

    @staticmethod
    def validate_date(date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False

# Клас для запису контакту
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if not any(p.value == old_phone for p in self.phones):
            raise ValueError("Phone number not found.")
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(str(p) for p in self.phones)
        birthday = str(self.birthday) if self.birthday else "Not set"
        return f"Contact name: {self.name}, phones: {phones}, birthday: {birthday}"

# Клас адресної книги
class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                # Перетворюємо рядок на об'єкт datetime для обчислень
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                # Визначаємо дату народження цього року
                birthday_this_year = birthday.replace(year=today.year)
                if birthday_this_year < today:
                    # Якщо день народження вже минув, беремо наступний рік
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                # Перевіряємо, чи день народження в межах 7 днів
                if today <= birthday_this_year <= next_week:
                    # Якщо день народження припадає на вихідний, переносимо на понеділок
                    congratulation_date = birthday_this_year
                    if birthday_this_year.weekday() >= 5:  # Субота (5) або неділя (6)
                        days_to_monday = 7 - birthday_this_year.weekday()
                        congratulation_date = birthday_this_year + timedelta(days=days_to_monday)
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime("%d.%m.%Y")
                    })

        return upcoming

# Парсинг введення користувача
def parse_input(user_input):
    return user_input.strip().split()

# Обробники команд
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    return "; ".join(str(phone) for phone in record.phones)

@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    if record.birthday is None:
        return "Birthday not set."
    return str(record.birthday)

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    return "\n".join(f"{entry['name']}: {entry['birthday']}" for entry in upcoming)

# Головна функція
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()