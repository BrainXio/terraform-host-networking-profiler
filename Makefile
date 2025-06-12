.PHONY: docs

docs:
	terraform-docs markdown table --header-from=docs/header.md --footer-from=docs/footer.md --output-file=README.md .
