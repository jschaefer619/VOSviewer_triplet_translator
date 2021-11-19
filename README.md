## Welcome!

This is a utility tool developed to translate .csv files into .json input for the [VOSviewer Online Application](https://app.vosviewer.com/)

VOSviewer is a software tool originally developed for constructing and analyzing bibliometric networks as network graphs. However, it is adaptable for many other uses. This utility tool serves as way to visualize spreadsheet data (.csv files) within VOSviewer.

Many features of this tool were originally developed for specific use with a curated dataset of semantic triplets. These triplets were generated as a part of ongoing research in [UCLA Prof Presner's Lab](https://holocaustresearchlab.com/). But this tool is appropriate for any dataset with the following general triplet structure:

Subject -> Verb -> Object

An example of this strucuture within our semantic triplet data:

We (Subject) -> had (Verb) -> A curfew (Object).

This structure can be adapted for many uses. Here's an example of this structure being implemented in social media related research...

User X -> Reposted -> Content from User Y.

### Dependencies

Most modules this tool uses are included in the standard Python 3 library. An exception is the popular Data Science tool Pandas. See [these tutorials](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html) for help with Pandas installation. An easy solution for those inexperienced with Python enviroments or command line tools is to install [Anaconda](https://anaconda.org/).

### Video Tutorial

For those who would like a step by step video walkthrough of the usage and features of the this repo, watch [this video.](https://youtu.be/-w1ttOpgBBc)

## Usage

This tool uses the command line interface. For using the tool, first navigate to this repository's directory. Then type

```
python vosviewer_triplet_translator.py -h
```

This will generate a help screen with a list of possible arguements.

```
usage: vosviewer_triplet_translator.py [-h] [-i INPUT_FILENAME]
                                       [-c CONTEXT_COL_NAME] [-v] [-o OUTPUT]
                                       [-f]
                                       node_col_name_1 edge_col_name
                                       node_col_name_2

positional arguments:
  node_col_name_1       column name of input file to be represented as node
                        (first of two inputs)
  edge_col_name         column name of input file to be represented as edges
                        (first of one input)
  node_col_name_2       column name of input file to be represented as node
                        (second of two inputs)

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILENAME, --input_filename INPUT_FILENAME
                        .csv input filepath to translate into VOSviewer
                        triplets
  -c CONTEXT_COL_NAME, --context_col_name CONTEXT_COL_NAME
                        column file to be represented as context
  -v, --verbosity
  -o OUTPUT, --output OUTPUT
                        argument for specifying output filepath location
  -f, --include_formatted_html
                        argument to determine if metadata should be included &
                        description formatted specific to Discrimination
                        Triplets
```

### For use with Specific Triplet Data

To run this tool on the default dataset, simply type in...

```
python vosviewer_triplet_translator.py subjects relations objects
```

This will utilize the triplet dataset included in the repository as input. This will then output the results in the 'output' directory.

The 3 arguments NODE_COL_NAME_1 EDGE_COL_NAME NODE_COL_NAME_2 are required. These arguments specify which column names within the input .csv file are to be represented as 'sending' nodes, edges, and 'receiving' nodes respectively.

All other arguements are optional.

A helpful arguement for use specifically with the included triplets is the -f or --include_formatted_html argument:

```
python vosviewer_triplet_translator.py subjects relations objects -f
```

This will make the .json output contain specialized metadata for the included dataset. However, this argument will throw an error if more general data is used as an argument.

#### A Note on Input and Output paths

Users can also specify specific input and output paths for this program.

```
python vosviewer_triplet_translator.py NODE_COL_NAME_1 EDGE_COL_NAME NODE_COL_NAME_2 -i INPUT_FILEPATH -o OUTPUT_FILEPATH
```

Be sure to use full filepath names.

Alternatively, users can manually drag and drop input .csv data into the /data directory. The application will then ask which input file to use.

### For use with General Data

As mentioned above, this program can be used with general triplet data. 

For demonstration, let's imagine we return to our example of using this tool for processing social media data.

In our hypothetical social_media_spreadsheet.csv file located on our desktop, there are four relevant columns...

user_1 |   action   |  user_1     | full_post 
------ | ---------- | ------------| ---------------------|
sally_s |   likes   | post_malone | "love the new album!"
jose_m  | retweeted |  david_64   | "nice pants!"

Within VOSviewer, we want to represent how some users interact with others through a network graph.

So, for our input within this tool, we would type:

```
python vosviewer_triplet_translator.py user_1 action user_1 -i "/Users/Desktop/social_media_spreadsheet.csv.csv"
```
Note that your specific input datapath would depend on your specific computer's OS, among other factors.

Note that each of these 3 positional arguments above corresponds with our input spreadsheet.

#### A note on the context arguement

You will notice there is an optional argument '-c' or '--context'.

Users have the option to include basic string metadata to be represented in VOSviewer to supplement the graph vizualization.

For our above social media example, relevant text based metadata is found as the 'full_post' column. It would be useful to have this metadata represented in our visualization.

So, we would type...

```
python vosviewer_triplet_translator.py user_1 action user_1 -i "/Users/Desktop/social_media_spreadsheet.csv.csv" -c full_post
```

Now, our Visualization will contain more useful metadata. Hooray!

### Troubleshooting

Be sure that your three positional arguments correspond to your input .csv file.

Remember, only use the -f optional argument when using the input data included in this repository.

Depending on the configeration of python on your local machine, using 'python3' instead of 'python' will resolve some issues with running the script. You should utilize whatever command runs the python enviroment with pandas and all the other necessary dependencies.

Additionally, feel free to reach out to me or to open an issue.


Happy Visualizing!




