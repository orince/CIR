## Dependencies
This code is written for Python (3.10.12) and makes use of the following packages:
torch: 1.13.1+cu117
numpy: 1.26.4
pandas: 2.2.2
scipy: 1.12.0
six: 1.16.0
scikit-learn: 1.1.2
rpy2: 3.5.10
jupyter_core: 5.3.1
notebook: 7.0.3
qtconsole: 5.4.4
IPython: 8.5.0
ipykernel: 6.16.0
jupyter_client: 8.3.1
jupyterlab: 4.0.5
nbconvert: 7.8.0
ipywidgets: 8.0.4
nbformat: 5.9.2
traitlets: 5.9.0
## Instructions

Our method 'ours.py' is implemented in the package contained within the "chr/" directory. 
CIR and CIR_rank(also CIR-FA) are the methods in the paper.

This can be loaded and utilized as demonstrated in the tutorial notebook "examples/example_aaai.ipynb".

Following is the same as CHR (we add parallel version: submit_experiment_real.py and the original one is named as 'old_submit_experiment_real.py'):
The Python code needed to reproduce our numerical experiments are in the "experiments/" directory,
along with bash scripts to submit the experiments, either sequentially (default), or on a computing cluster with a slurm interface.

make_plots_real.R/make_plot.R  --> boxplots,
submit_experiment_real.py/submit_experiment.py --> tables


The script "experiments/dataset.py" loads and pre-processes the real data sets, which can be dowloaded freely from the sources referenced in the accompanying paper. 