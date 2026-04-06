import pickle
from datetime import datetime,timedelta
from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None 
    
    def add_phone(self, phone_number: str):
        new_phone = Phone(phone_number)
        self.phones.append(new_phone)
    
    
    def add_birthday(self, birthday_value: str):
        self.birthday = Birthday(birthday_value)
    

    def find_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def edit_phone(self, old_phone: str, new_phone: str):
        phone_obj = self.find_phone(old_phone)
        if phone_obj is None:
            raise ValueError("Phone not found")
        
        index = self.phones.index(phone_obj)
        self.phones[index] = Phone(new_phone)

    def remove_phone(self, phone_number: str):
        phone_obj = self.find_phone(phone_number)
        if phone_obj is not None:
            self.phones.remove(phone_obj)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, Birthday: {self.birthday}"

class AddressBook(UserDict):
    
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):

        return self.data.get(name)

    def delete(self, name: str):
 
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthday = []
        for record in self.data.values():
            if record.birthday:
                b_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                b_this_year = b_date.replace(year = today.year)
                if b_this_year < today:
                    b_this_year = b_this_year.replace(year = today.year + 1)
                delta_days = (b_this_year - today).days       
                if 0 <= delta_days <= 7:
                    greet_date = b_this_year
                    if greet_date.weekday() == 5:
                        greet_date += timedelta(days = 2)
                    elif greet_date.weekday() == 6:
                        greet_date += timedelta(days = 1)
                    upcoming_birthday.append({
                        "name": record.name.value,
                        "birthday": greet_date.strftime("%d.%m.%Y")
                    })
        return upcoming_birthday



    def __str__(self):
     
        if not self.data:
            return "Address Book is empty."
        return "\n".join(str(record) for record in self.data.values())

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                return "Error: Please provide all required arguments."
            return str(e)
        except KeyError:
            return "Error: Contact not found."
        except IndexError:
            return "Error: Not enough arguments provided."
        except Exception as e:
            return f"Unexpected error: {e}"
    return inner 
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

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
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact phone updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    if not record.phones:
        return f"No phones found for {name}."
    # Використовуємо одинарні лапки всередині f-рядка
    return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())
    
@input_error
def add_birthday_handler(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(birthday)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    if record.birthday is None:
        return f"No birthday set for {name}."
    return f"{name}'s birthday is {record.birthday.value}"

@input_error
def birthdays_handler(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays for the next 7 days."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)  

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        # Запобігаємо помилці, якщо користувач просто натиснув Enter
        if not user_input.strip():
            continue
            
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
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
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday_handler(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays_handler(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()