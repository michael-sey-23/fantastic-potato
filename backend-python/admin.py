import json
import os

from dotenv import load_dotenv

from utils import add_new_entry, update, delete

load_dotenv()


def confirm_entry(entry="", by_admin=True, user_entry=""):
    """
    Confirm a user's entry
    Parameters:
        entry: The type of entry being added (Acronym, definition, description)
        by_admin: Determines if the entry is made by an admin or a general user.
            If by_admin is set to true, then go through the confirmation process.
            Else just show the text entered.
        user_entry: The data being entered
    Returns:
        str: The text the user entered
    """
    confirm = False
    check = ""

    if by_admin:
        user_input = input(f"Enter {entry}: ")
        while not confirm: # Flag to check if user is satisfied with their input
            while check not in ["y", "n"]:
                check = input(f"You entered '{user_input}', is this correct? (y/n): ").lower()
                if check == "y":
                    confirm = True
                else:
                    user_input = input(f"Re-enter {entry}: ")
                    check = ""
        return user_input

    else:
        print(f"User entry: {user_entry}")
        return user_entry


if __name__ == "__main__":
    choice = " "
    while choice not in ["1", "2", "3", "4", "5"]:
        choice = input(
            "1. Add a new acronym\n2. Update an entry\n3. Delete an entry\n4. Review Entries\n5. Exit\nChoose an option: ")
        if choice not in ["1", "2", "3", "4", "5"]:
            print("Invalid choice, please try again.")

    # Adding new acronym entry
    if choice == "1":
        acronym = confirm_entry(entry="acronym")
        definition = confirm_entry(entry="definition")
        description = confirm_entry(entry="description")
        add_new_entry(acronym, definition, description)

    # updating entry
    elif choice == "2":
        acronym = confirm_entry(entry="acronym")
        definition = confirm_entry(entry="definition")
        description = confirm_entry(entry="description")
        update(acronym, definition, description)

    # Delete entry
    elif choice == "3":
        acronym = confirm_entry(entry="acronym")
        delete(acronym)

    # Review entries to be added
    elif choice == "4":

        if not os.path.exists(os.getenv("REVIEW_LIST")):
            print("No entries to review yet.")
        else:
            review_file = os.getenv("REVIEW_LIST")
            rejected_entries = []
            with open(review_file, "r") as file:
                data = json.load(file)

            for entry in data:
                # Extract necessary data from the json file
                acronym = confirm_entry(by_admin=False, user_entry=entry["acronym"])
                # If new_acronym is true, that means they are adding a new acronym. Otherwise it is an updated term
                new_acronym = entry["metadata"]["new_acronym"]

                # Check if admin wants to accept the user's entry / suggested update
                accept = ""
                while accept not in ["y", "n"]:
                    accept = input("Do you accept the entry? (y/n): ").lower()
                if accept == "y":
                    if new_acronym:
                        definition = confirm_entry(entry="definition")
                        description = confirm_entry(entry="description")
                        add_new_entry(acronym, definition, description)
                    else:
                        definition = confirm_entry(entry="definition")
                        description = confirm_entry(entry="description")
                        update(acronym, definition, description)
                    print(f"Entry '{acronym}' accepted.\n")
                else:
                    rejected_entries.append(entry)
                    print(f"Entry '{acronym}' rejected.\n")

            # Determine whether to keep the rejected entries in the json file
            keep_rejected = ""
            while keep_rejected not in ["y", "n"]:
                keep_rejected = input("Do you want to clear the review list? (y/n): ").lower()

            if keep_rejected == "n":
                with open(review_file, "w") as file:
                    json.dump(rejected_entries, file, indent=4)
            else:
                with open(review_file, "w") as file:
                    json.dump([], file, indent=4)


    # Exit
    else:
        print("Goodbye...")
