.PHONY: build

build:
	pyinstaller cli.py \
		--name oc-hibernate \
		--add-data "./playbooks:./playbooks" \
		--onefile

clean:
	rm -rf build dist *.spec

install:
	cp ./dist/oc-hibernate "${HOME}/bin"
