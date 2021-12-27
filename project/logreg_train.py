import os.path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
import time
from datetime import datetime as dt

# TODO make as parameters
MAX_DF = 0.7
MIN_DF = 5
N_JOBS = -1
INPUT_DIR = "./data"
OUTPUT_DIR = "./logreg_train/output"


class Timeit(object):
    def __init__(self, description):
        self.description = description

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        ex_time = time.time() - self.start_time
        print(self.description, ex_time, "seconds")
        return True


def read_dataset(input_dir, subset):
    """
    Reads and drops NAs
    :param input_dir: where the (train.csv, test.csv, valid.csv, ...) are located
    :param string subset: the name of the subset to read (train, test, valid, ...)
    :return: pd.DataFrame
    """
    df = pd.read_csv(os.path.join(input_dir, f"{subset}.csv"), header=0)
    initial_shape = df.shape[0]
    df = df.dropna(how="any")
    curr_shape = df.shape[0]
    print(f"There were {curr_shape - initial_shape} empty examples dropped.",
          f"{subset.upper()} set has {curr_shape} rows.")
    return df


if __name__ == '__main__':

    logreg = Pipeline(steps=[("vectorizer", TfidfVectorizer(max_df=MAX_DF, min_df=MIN_DF)),
                             ("log_reg", LogisticRegression(n_jobs=N_JOBS,
                                                            solver="saga",
                                                            multi_class="multinomial",
                                                            random_state=100500))],
                      verbose=True)

    # load the data & filter the pos
    (train, valid, test) = (read_dataset(INPUT_DIR, subset) for subset in ["train", "valid", "test"])

    # train the pipeline
    logreg.fit(train["description"], train["targetcat"])
    suffix = dt.now().isoformat("-")
    output_dir = os.path.join(OUTPUT_DIR, suffix)

    vectorizer = logreg.named_steps["vectorizer"]
    joblib.dump(vectorizer, os.path.join(output_dir, "tf_idf_vectorizer"), compress=3)

    for name, step in logreg.named_steps:
        joblib.dump(step, os.path.join(output_dir, f"{name}.joblib"), compress=3)

    # evaluation on validation
    val_preds = logreg.predict(valid["description"])
    val_f1_scores_by_category = f1_score(valid["targetcat"], val_preds, average=None)
    val_f1_score_macro = np.mean(val_f1_scores_by_category)
    print(f"F1 Macro on validation is: {val_f1_score_macro}")