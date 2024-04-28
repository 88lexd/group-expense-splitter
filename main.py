from person import Person
import validation as v
import math
import yaml
import sys


def main():
    print("===============================")
    print("Group Expense Splitter Script")
    print("Author: Alex Dinh")
    print("===============================\n")

    try:
        expenses_file = sys.argv[1]
    except IndexError:
        print("Error: at least one argument is required to specify the input file.")
        sys.exit(1)

    print(f"Reading expenses from {expenses_file}")
    all_expenses = read_yaml(expenses_file)
    v.validate_yaml(all_expenses)

    print("Building instance for each person...")
    group = dict()
    for person in all_expenses['people']:
        group.update({
            person.upper(): Person(
                    name=person,
                    expenses=all_expenses['expenses'].get(person, None)
                    )
            }
        )

    print("Adding up expenses for each person...")

    print("\n===============")
    print("Expense Details")
    print("===============")
    calculate_all_expenses(group)

    print("\n=========================")
    print("Group Debt/Credit Totals")
    print("=========================")
    show_debt_credit_info(group)

    print("\n=========================")
    print("Group Payout Information")
    print("=========================")
    creditors, debtors = get_creditors_and_debtors(group)
    calculate_payments(creditors, debtors)

    print('\nScript Completed!')


def calculate_payments(creditors: list, debtors: list) -> None:
    # Set final balance now that the debt/credit is fully updated
    [i.set_final_balance() for i in creditors]
    [i.set_final_balance() for i in debtors]

    for creditor in creditors:
        while round(creditor.final_balance, 2) > 0.00:
            for debtor in debtors:
                if debtor.final_balance == 0:
                    # Debtor is not owing any money. Skip..
                    continue

                if (creditor.final_balance + debtor.final_balance) > 0:
                    balance_str = '{0:.2f}'.format(debtor.final_balance * -1)
                    print(f" - {debtor.name} pays {creditor.name} ${balance_str}")
                    credit_final_balance_rounded = round(creditor.final_balance + debtor.final_balance, 3)
                    creditor.final_balance = credit_final_balance_rounded
                    debtor.final_balance = 0
                    # Debtor has paid all debt, continue to next debtor
                    continue
                else:
                    balance_str = '{0:.2f}'.format(creditor.final_balance)
                    print(f" - {debtor.name} pays {creditor.name} ${balance_str}")
                    debtor.final_balance = round(debtor.final_balance + creditor.final_balance, 3)
                    creditor.final_balance = 0
                    # Creditor is fully paid, break out of debtor loop
                    break


def get_creditors_and_debtors(group: dict) -> tuple[list, list]:
    creditors = list()
    debtors = list()
    for name, person in group.items():
        if person.in_debt():
            debtors.append(person)
        else:
            creditors.append(person)

    return creditors, debtors


def show_debt_credit_info(group: dict) -> None:
    for name, person in group.items():
        if person.in_debt():
            balance_str = '{0:.2f}'.format(person.balance() * -1)
            print(f"{name} owes ${balance_str} to the group money based on:")
        else:
            balance_str = '{0:.2f}'.format(person.balance())
            print(f"{name} is receiving ${balance_str} from the group based on:")
        print(f" - Credit: ${'{0:.2f}'.format(person.credit)}")
        print(f" - Debt: -${'{0:.2f}'.format(person.debt)}")


def calculate_all_expenses(group: dict) -> None:
    group_total_expense = 0
    for name, person in group.items():
        if person.expenses is None:
            print(f"{name} has no expenses")
            continue

        print(f"{name} has spent:")
        person_total_expenses = 0
        for item, details in person.expenses.items():
            # Build display string for items split with specific individuals.
            if 'split_with' in details.keys():
                split_with_str = f"(split with: {', '.join(details['split_with'])})"
                calculate_split_debt(group, details['split_with'], float(details['amount']))
            else:
                split_with_str = ''
                calculate_all_debt(group, float(details['amount']))

            # Add expense as credit to the person made the expense
            person.add_credit(float(details['amount']))

            print(f" - ${details['amount']} on {item} {split_with_str}")
            person_total_expenses += float(details['amount'])

        group_total_expense += person_total_expenses

    group_total_expense_str = '{0:.2f}'.format(group_total_expense)
    print(f"\nThe group has spent a total of: ${group_total_expense_str}")


def calculate_split_debt(group: dict, split_with: list, amount: float) -> None:
    # Accumulate debt for those splitting the expense
    split_between_number = len(split_with)
    debt_per_person = float(amount / split_between_number)
    debt_per_person_rounded = round(debt_per_person, 3)
    for person in split_with:
        group[person.upper()].add_debt(debt_per_person_rounded)


def calculate_all_debt(group: dict, amount: float) -> None:
    # General expenses are split between everyone
    split_between_number = len(group)
    debt_per_person = float(amount / split_between_number)
    debt_per_person_rounded = round(debt_per_person, 3)
    for person in group:
        group[person.upper()].add_debt(debt_per_person_rounded)


def read_yaml(input_file: str) -> dict:
    with open(input_file, 'r') as f:
        try:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            return config
        except yaml.YAMLError as exc:
            print(exc)
            raise Exception(f"Cannot parse {input_file} file")


if __name__ == "__main__":
    main()
