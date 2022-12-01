.PHONY: build

build:
	pyinstaller cli.py --onefile --name oc-hibernate

clean:
	rm -rf build dist *.spec
