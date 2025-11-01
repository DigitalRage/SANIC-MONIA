import os
collom=0
print(os.get_terminal_size(collom))
collom,row=os.get_terminal_size()
print(collom,row)
for x in range(os.get_terminal_size()[5:6]):
	print(x)