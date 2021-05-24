# import self_writing

self_writing_path = "C:\\Users\\tmrup\\Documents\\entente\\Entente\\self_writing.py"
file = open(self_writing_path, "w")
new_code = compile("def my_function(x):\n\treturn x + 1",  "", 'exec')
eval(new_code)

print (my_function(24))

new_function = "def my_function(x):\n\treturn x + 32"
file.write(new_function)
new_code = compile("def my_function(x):\n\treturn x + 32",  "", 'exec')
eval(new_code)

print (my_function(53))