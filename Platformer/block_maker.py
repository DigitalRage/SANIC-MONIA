import random
def print_block():
    for x in range(20):
        for x in range(20):
            var=random.randint(1,10)
            #if var<=9:
            #    print("🟫",end="")
            #elif var==9:
            #    print("⬛️",end="")
            #elif var==8:
            #    print("⬜️",end="")
            if var>=3:
                print("🟥",end="")
            #elif var==6:
            #    print("🟪",end="")
            #elif var==5:
            #    print("🟦",end="")
            #elif var==4:
            #    print("🟩",end="")
            elif var==2:
                print("🟨",end="")
            elif var==1:
                print("🟧",end="")
            #elif var==1:
            #    print("🔲",end="")
        print()

print_block()