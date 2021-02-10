def read_first_line(file):
	with open(file, "r") as f:
		return f.readlines()[0]