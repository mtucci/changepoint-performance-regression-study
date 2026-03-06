#!/bin/bash

# Setup the python virtual environment if not already done
setup() {
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        deactivate
    fi
    source .venv/bin/activate
}

# Convert annotations from CSV to JSON format and create summaries for datasets.
convert_annotations() {
    annotations=$1
    grep -v demo $annotations > tmp_annotations.csv
    python annotations_to_json.py tmp_annotations.csv
    mv tmp_annotations.json annotations.json
    rm tmp_annotations.csv
}

# Generate summary for a dataset using the results from the specified directory.
summary() {
    dataset=$1
    results=$2
    python summarize.py -a annotations.json -d $dataset -r $results \
        > summaries/$(basename $dataset)
}

# Create summaries for all datasets in the specified directory.
create_summaries() {
    annotations=$1
    datasets=$2
    results=$3
    mkdir -p summaries

    for dataset in $(tail -n+2 $annotations | cut -d, -f2 | grep -v demo)
    do
        if [[ ! -f "summaries/${dataset}.json" ]]
        then
            summary $datasets/${dataset}.json $results
            echo "Processing dataset: $dataset"
        fi
    done

}

###
if [ "$#" -ne 3 ]
then
    echo "Usage: $0 <annotations CSV> <datasets dir> <results dir>"
    exit 1
fi

annotations=$1
datasets=$2
results=$3

setup

echo "Converting annotations from CSV to JSON format..."
[[ ! -f annotations.json ]] && convert_annotations $annotations

echo "Creating summaries of the execution of methods on the time series..."
create_summaries $annotations $datasets $results

echo "Converting summaries to CSV format..."
[[ ! -f summaries.csv ]] && python summaries_to_csv.py summaries

echo "Generating a table of methods scores (Table 5) for RQ3..."
python methods_scores.py summaries.csv

deactivate
