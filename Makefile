.PHONY: run db clean
.ONESHELL:

DATABASE_FILE ?= "/tmp/test.db"
METADATA_DIR ?=

run: db
	FLASK_APP=mcarch/app.py FLASK_ENV=development \
	MCARCH_CONFIG=dev_config.py \
	flask run

db:
	@[[ -f $(DATABASE_FILE) ]] && exit 0
	echo "Importing Metadata..."
	@MCARCH_CONFIG=dev_config.py python mkdb.py $(METADATA_DIR) 2>&1 >/dev/null

clean:
	rm $(DATABASE_FILE)
