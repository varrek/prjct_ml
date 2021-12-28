import argparse
import logging
import os
import pandas as pd
from sklearn.model_selection import train_test_split


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# Since we get a headerless CSV file we specify the column names here.
features = ["title", "description"]
label_column = "deep_category_minus_one"


if __name__ == "__main__":
    random_seed = 100500
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-data", type=str, required=True)
    args = parser.parse_args()

    #TODO with argparse
    group_size = 100

    logger.debug("Starting preprocessing.")

    base_dir = "./data"
    output_dir = base_dir
    input_data = args.input_data

    df = pd.read_parquet(input_data)

    sample = df.sort_values([label_column], ascending=True)\
               .groupby(label_column).head(group_size)
    v = sample[label_column].value_counts()
    # The least populated class in y has only 1 member, which is too few. The minimum
    # number of groups for any class cannot be less than 2.
    # We have six (x, y train; x, y test; x, y val)
    sample = sample[sample[label_column].isin(v.index[v.gt(6)])]

    classes = sample[label_column].unique()
    columns_to_drop =  sample.columns[~sample.columns.isin(features)]
    X_train, X_rest, y_train, y_rest = train_test_split(sample.drop(columns_to_drop, axis=1),
                                                        sample[label_column],
                                                        test_size=0.25,
                                                        random_state=random_seed,
                                                        stratify=sample[label_column])
    X_val, X_test, y_val, y_test = train_test_split(X_rest,
                                                    y_rest,
                                                    test_size=0.5,
                                                    random_state=random_seed,
                                                    stratify=y_rest)
    train = X_train.assign(targetcat=y_train)
    valid = X_val.assign(targetcat=y_val)
    test = X_test.assign(targetcat=y_test)

    logger.info("Writing out datasets to %s.", output_dir)
    train.to_csv(os.path.join(output_dir, "train.csv"), index=False)
    valid.to_csv(os.path.join(output_dir, "valid.csv"), index=False)
    test.to_csv(os.path.join(output_dir, "test.csv"), index=False)

