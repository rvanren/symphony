all: dependencies gen parser
	rm -rf build/  # Remove previous build files
	python3 setup.py build_ext -i

type-check:
	# Excluding DumpASTVisitor because mypy cannot infer inheritance where a derived class
	# uses named arguments while the base class uses kwargs.
	mypy symphony \
		symphony_model_checker/compile.py \
		symphony_model_checker/config.py \
		symphony_model_checker/dfacmp.py \
		symphony_model_checker/exception.py \
		symphony_model_checker/iface.py \
		symphony_model_checker/main.py \
		symphony_model_checker/symphony \
		symphony_model_checker/util \
		symphony_model_checker/parser/antlr_rule_visitor.py \
		symphony_model_checker/parser/custom_denter.py \
		symphony_model_checker/parser/SymphonyErrorListener.py \
		--exclude symphony_model_checker/symphony/DumpASTVisitor.py \
		--follow-imports silent \
		--check-untyped-defs \
		--allow-untyped-defs \
		--python-version 3.8 \
		--html-report mypy-report \
		--txt-report mypy-report

parser:
	java -jar antlr-4.9.3-complete.jar -Dlanguage=Python3 -visitor Symphony.g4 -o symphony_model_checker/parser -no-listener

dependencies:
	- python3 -m pip install -r requirements.txt

gen:
	printf "\n__package__ = \"symphony_model_checker\"\n" > symphony_model_checker/__init__.py
	printf "__version__ = \"1.2.%d\"\n" `git log --pretty=format:'' | wc -l | sed 's/[ \t]//g'` >> symphony_model_checker/__init__.py
	chmod +x symphony

charm:
	gcc -Isymphony_model_checker/charm -Isymphony_model_checker/charm/iface -o charm.exe -pthread symphony_model_checker/charm/*.c symphony_model_checker/charm/iface/*.c

behavior: x.hny
	./symphony -o x.hny
	: ./symphony -mqueue=queueconc code/qtestconc4.hny
	: ./symphony code/qtestconc4.hny
	: python3 behavior.py -Tdot -M x.hco
	open x.png

iface: iface.py iface.json
	./symphony -i 'countLabel(cs)' code/csonebit.hny
	: ./symphony -i 'countLabel(cs)' code/Peterson.hny
	: ./symphony -i '(flags,turn)' code/Peterson.hny
	: ./symphony -i rw code/RWtest.hny
	python3 iface.py iface.json > x.gv
	dot -Tpdf x.gv > x.pdf
	open x.pdf

dist: gen parser
	rm -rf build/ dist/ symphony_model_checker.egg-info/
	python3 setup.py sdist

upload-test: dist upload-env
	source .upload_env testing && twine upload --non-interactive --verbose -r testpypi dist/*

install-test:
	pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.python.org/simple symphony

upload: dist upload-env
	source .upload_env release && twine upload --non-interactive --verbose -r pypi dist/*

upload-env:
ifeq ("$(wildcard .upload_env)", "")
	$(error Missing .upload_env file. Create one using .upload_env.template)
endif

clean:
	rm -f code/*.htm code/*.hvm code/*.hco code/*.png code/*.hfa code/*.tla code/*.gv *.html
	(cd symphony_model_checker/modules; rm -f *.htm *.hvm *.hco *.png *.hfa *.tla *.gv *.html)
	rm -rf compiler_integration_results.md compiler_integration_results/
	rm -rf build/ dist/ symphony_model_checker.egg-info/
