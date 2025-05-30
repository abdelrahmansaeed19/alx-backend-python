rows = input("Enter the number of rows: ")
rows = int(rows)

for i in range(rows):

    for j in range(rows - i):
        print(" ", end="")

    for j in range(2*i + 1):
        print("*", end="")
    
    print("")