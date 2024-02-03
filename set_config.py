import pickle

print("DANGER: If you don't know what you are doing, press Ctrl-C to exit this program!")
print()
print("setting config file")

cookie = input("cookie> ")
with open("config.pickle", "wb") as file:
    pickle.dump({"cookie": cookie}, file)
