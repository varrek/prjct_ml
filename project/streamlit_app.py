import joblib
import numpy as np
import s3fs
import streamlit as st
import tensorflow_hub as hub
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
import tensorflow_text
import tensorflow as tf
from tensorflow import keras
class MyDict(dict):
    def __missing__(self, key):
        return None
fs = s3fs.S3FileSystem(anon=False)
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")

vectorizer = joblib.load("models/logreg_all_data_with_cats_gt_50/tf_idf_vectorizer.joblib")
model = joblib.load("models/logreg_all_data_with_cats_gt_50/model_log_reg.joblib")
df = joblib.load('models/usem_all_data_with_cats_gt_50/df_cats.joblib')


def clear_usem_predict(text):
    embed_text = np.asarray(embed(text))
    cos_sim = cosine_similarity(embed_text, df['cat_embeding'].tolist())
    indexes = np.argmax(cos_sim, axis=1)
    cats = df.loc[indexes]['cat_name']

    return cats


def logreg_predict(text):
    logreg = Pipeline(steps=[("vectorizer", vectorizer),
                             ("log_reg", model)
                             ],
                      verbose=True)

    return logreg.predict([text])


def process_prediction(text, prediction):
    if st.button("Click Here to Classify"):

        if not text:

            st.write("Please add a description to Classify")

        else:
            with st.spinner('Classifying ...'):
                st.write(prediction)

                st.success('Done!')

            st.sidebar.header("Algorithm Predicts: ")
            st.sidebar.write(prediction)


def main():
    st.title("Product Classifer ML App")
    st.subheader("NLP and ML App with Streamlit")
    # Textbox for text user is entering
    # Picking what NLP task you want to do
    option = st.selectbox('NLP Service', (
        'USE classifier without training', 'Tensorflow USE',
        'Logistics regression'))  # option is stored in this variable
    st.subheader("Enter the product description you'd like to classify.")
    text = st.text_area("Enter product description", placeholder="Type Here")
    # Display results of the NLP task
    if option == 'Logistics regression':
        prediction = logreg_predict(text)
        process_prediction(text, prediction)
    elif option == 'USE classifier without training':
        prediction = clear_usem_predict(text)
        process_prediction(text, prediction)
    elif option == 'Tensorflow USE':
        new_model = tf.keras.models.load_model('models/usem_all_data_with_cats_gt_50')
        mapping_dict = joblib.load('models/usem_all_data_with_cats_gt_50/mapping_dict_reverse')
        prediction = new_model.predict([text])
        index = np.argmax(prediction)
        prediction = mapping_dict[index]
        process_prediction(text, prediction)


if __name__ == '__main__':
    main()
