.PHONY: build

build:
	pyinstaller cli.py --onefile --name oc_hibernate
