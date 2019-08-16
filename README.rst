Uses poetry

# Running the source locally
1. `poetry run python dj`

# Testing the source
1. `poetry run pytest`

# To build and install locally
1. `poetry build && pip3 install --user --upgrade --force-reinstall dist/dj-0.1.0-py3-none-any.whl`

# To publish
1. `poetry publish --build --username USERNAME --password PASSWORD`
