.PHONY: build

build:
	pyinstaller cli.py \
		--name oc-hibernate \
		--add-data "./playbooks/test.yml:./playbooks" \
		--onefile

clean:
	rm -rf build dist *.spec
