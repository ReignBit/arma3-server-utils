import os

# Execute the renaming of files
print("Removing uppercase...")
os.system("find . -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;")

# Do the remove of space and other characters arma doesnt like
print("Removing special characters...")
for modfolder in os.listdir("."):
    if modfolder.startswith("@"):
        # Is mod folder
        renamed = modfolder.replace(" ", "_").replace("!", "").replace("(","").replace(")", "").replace("[","").replace("]", "")
        if renamed != modfolder:
            print(modfolder, " -> ", renamed)
            os.rename(modfolder, renamed)
