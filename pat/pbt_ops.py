import os
print ("Current Directory =", os.getcwd())
print("cd pat")
os.chdir("pat")
print ("Current Directory =", os.getcwd())
print ("Contents of ", os.getcwd(), ":")
os.system("dir")
print("Executing pb_tool compile")
os.system("pb_tool compile")
print("Executing pb_tool deploy")
os.system("pb_tool deploy -y")
print("Executing pb_tool zip")
os.system("pb_tool zip")
print ("Contents of ", os.getcwd(), ":")
os.system("dir")
print ("Contents of ", os.path.join(os.getcwd(),"pat"), ":")
os.system("dir pat")