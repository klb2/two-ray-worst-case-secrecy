# Worst-Case Secrecy Rate Optimization for Two-Ray Scenarios

This repository is accompanying the paper "Frequency Diversity for
Ultra-Reliable and Secure Communications in Sub-THz Two-Ray Scenarios" (Karl-L.
Besser, Eduard Jorswieck, and Justin Coon, IEEE ICC 2023.
[doi:10.1109/ICC45041.2023.10279098](https://doi.org/10.1109/ICC45041.2023.10279098)).

The idea is to give an interactive version of the calculations and presented
concepts to the reader. One can also change different parameters and explore
different behaviors on their own.


[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/klb2/two-ray-worst-case-secrecy/HEAD)

## File List
The following files are provided in this repository:

- `run.sh`: Bash script that reproduces the figures presented in the paper.
- `util.py`: Python module that contains utility functions, e.g., for saving results.
- `model.py`: Python module that contains utility functions around the two-ray
  ground reflection model.
- `single_frequency.py`: Python module that contains the functions to calculate
  the receive power when a single frequency is used.
- `two_frequencies.py`: Python module that contains the functions to calculate
  the receive power when two frequencies are used in parallel.
- `optimal_frequency_distance.py`: Python module that contains the algorithm to
  calculate the optimal frequency spacing for worst-case design.
- `rates.py`: Python module that contains the functions to calculate and show
  the worst-case rates for the eavesdropper, i.e., the upper bounds.
- `secrecy_rate.py`: Python module that contains functions to calculate the
  secrecy rates.
- `conditions_positive_zosc.py`: Python module that contains the functions to
  check the necessary and sufficient conditions whether a positive ZOSC is
  possible.


## Usage
### Running it online
The easiest way is to use services like [Binder](https://mybinder.org/) to run
the notebook online. Simply navigate to
[https://mybinder.org/v2/gh/klb2/two-ray-worst-case-secrecy/HEAD](https://mybinder.org/v2/gh/klb2/two-ray-worst-case-secrecy/HEAD)
to run the notebooks in your browser without setting everything up locally.

### Local Installation
If you want to run it locally on your machine, Python3 and Jupyter are needed.
The present code was developed and tested with the following versions:

- Python 3.10
- Jupyter 1.0
- numpy 1.22
- scipy 1.8

Make sure you have [Python3](https://www.python.org/downloads/) installed on
your computer.
You can then install the required packages (including Jupyter) by running
```bash
pip3 install -r requirements.txt
jupyter nbextension enable --py widgetsnbextension
```
This will install all the needed packages which are listed in the requirements 
file. The second line enables the interactive controls in the Jupyter
notebooks.

Finally, you can run the Jupyter notebooks with
```bash
jupyter notebook
```

You can also recreate the figures from the paper by running
```bash
bash run.sh
```


## Acknowledgements
This research was supported by the Federal	Ministry of Education and Research
Germany (BMBF) as part of the 6G Research and Innovation Cluster 6G-RIC under
Grant 16KISK031 and by the EPSRC under grant number EP/T02612X/1.


## License and Referencing
This program is licensed under the GPLv3 license. If you in any way use this
code for research that results in publications, please cite our original
article listed above.

```bibtex
@inproceedings{Besser2023,
  author = {Besser, Karl-Ludwig and Jorswieck, Eduard A. and Coon, Justin P.},
  title = {Frequency Diversity for Ultra-Reliable and Secure Communications in Sub-{THz} Two-Ray Scenarios},
  booktitle = {ICC 2023 -- IEEE International Conference on Communications},
  year = {2023},
  month = {5},
  pages = {5817--5823},
  publisher = {IEEE},
  doi = {10.1109/ICC45041.2023.10279098},
}
```
