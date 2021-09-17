default: clean examples

examples:
	mkdir figs
	python3 ./plot_examples.py

install-dependencies:
	pip install numpy scipy matplotlib 

clean:
	rm -rf figs
