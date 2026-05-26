# dd2525-project

The goal of the project is to analyze the top 50 Golang packages by the number of GitHub stars they have. The analysis will look at capability models for each project using Capslock. Capslock analyzes Golang code and looks at what capabilities a program actually uses. How have the capabilities as modeled by our capabilities model of each version changed over time, and why?

See more about the background of the project in the [project proposal](project_proposal.pdf).

## Full report

See finalized report [here](report.pdf).

## Running the project

Before you start, ensure you have Docker running. To run the analysis, start by cloing the GitHub projec (see [this](https://github.com/settings/tokens)). This is not a requirement, but you may run into rate limits when fetching data from the GitHub API. Using an authenticated token, this limit is significantly higher. Export your token as an environment variable called `GITHUB_TOKEN`.

```
export GITHUB_TOKEN="your token here"
```

If you have [direnv](https://direnv.net/), a Python Virtual Environment will be created automatically. If you do not, it is recommended to create one. Install the requirements for running the scripts and the Jupyter Notebook.

```
pip install -r requirements.txt
pip install -r analysis/requirements.txt
```

Run the `fetch_toplist.py` to fetch a list of GitHub repositories.

```
python fetch_toplist.py
```

The list is saved in `toplist_repositories.txt`. The analysis is performed on repositories listed in `curated_toplist_repositories.txt` which is committed in the repository.

Run the `orchestrator.py` script to perform the analysis inside Docker. This can take some time.

```
python orchestrator.py
```

Once the script has finished, start Jupyter Lab in the analysis folder.

```
cd analysis
jupyter lab .
```

Run the notebook `notebook.ipynb` to perform the analysis and get the results.

## Authors

- Vilhelm Prytz <vprytz@kth.se>
- Filip Dimitrijevic <filipdi@kth.se>

## License

Licensed under MIT according to [LICENSE](LICENSE).
