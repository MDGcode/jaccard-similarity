import random
import string

def generate_names(filename, num_names=1000000, middle_prob=0.3):
    # Generates a file with random names.
    # Now we optionally add middle names instead of random letter suffixes.
    print(f"Generating {num_names} names into {filename} (middle name probability={middle_prob})...")
    
    first_names = ["Ion", "Maria", "Elena", "Andrei", "Alexandru", "Ioana", "Stefan", "Mihai", "George", "Ana", "Cristian", "Dan", "Vasile", "Constantin", "Gheorghe", "Florin", "Adrian", "Gabriel", "Nicolae", "Radu", "Bogdan", "Catalin", "Marian", "Viorica", "Mihaela", "Roxana", "Daniela", "Cristina", "Alina", "Luminita", "Iuliana"]
    last_names = ["Popescu", "Ionescu", "Radu", "Dumitrescu", "Stan", "Stoica", "Gheorghe", "Matei", "Ciobanu", "Ilie", "Rusu", "Serban", "Lazar", "Florea", "Tudor", "Dima", "Toma", "Gavrila", "Iancu", "Avram", "Mocanu", "Manole", "Badea", "Oprea", "Roman", "Marin"]
    # Middle names list (can reuse first names for realism)
    middle_names = ["Alex", "Luca", "Paul", "Marius", "Ioana", "Elisa", "Victor", "Cristi", "Andra", "Diana", "Ilinca", "Roxana", "Teodor", "Raluca", "Silviu"]

    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(num_names):
            # Random combinations of existing names to create a large dataset
            first = random.choice(first_names)
            last = random.choice(last_names)
            # Optionally add a middle name based on probability
            if random.random() < middle_prob:
                middle = random.choice(middle_names)
                f.write(f"{first} {middle} {last}\n")
            else:
                f.write(f"{first} {last}\n")

            if i % 100000 == 0 and i > 0:
                print(f"Generated {i} names...")

    print("Generation complete.")

if __name__ == "__main__":
    import sys
    count = 1000000
    middle_prob = 0.3
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    if len(sys.argv) > 2:
        try:
            middle_prob = float(sys.argv[2])
        except ValueError:
            pass
    generate_names("names.txt", count, middle_prob)
