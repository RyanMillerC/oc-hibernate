.PHONY: build

build:
	pyinstaller cli.py --onefile --name oc_hibernate

clean:
	rm -rf build dist *.spec
