release:
	./setup.py test && ./setup.py sdist && ./setup.py bdist_wheel && twine upload dist/* && git push && git push --tags

clean:
	rm -rf dist/

test:
	pytest -xvv

lint:
	pycodestyle --statistics --show-source --exclude=.env,.tox,dist,docs,build,*.egg .

xmllint:
	xml/validate.sh

clear-objects:
	python -c "from coralillo import Engine; eng=Engine(); eng.lua.drop(args=['*'])"
	mongo cacahuate --eval "db.history.drop()"
