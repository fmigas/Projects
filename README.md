Here you will find all my projects that I belive are worth seeing. 
I put only my own projects here - nothing is just copied from the Internet.

UKRAINIAN TWEETS

In this notebook, I analyze 100.000 tweets on Ukraine and classify them as written by „expert” or „not expert”.

The notebook goes through the whole process from defining a problem, data gathering, EDA, data preprocessing, feature engineering to different model validation.

Text data was processed with count vectorizer, tfidf (with and without chi2 selection), and keras tokenizer.

Models validated:
1. Sklearn library - logistic regression, naive bases, tree family models, 
2. Keras/TensorFlow - functional API models with two streams of input data, using embedding and convolutional layers
3. BERT fine-tuned model

Some observations on the usability of different metrics for an unbalanced data set.

NAMES GENERATOR

It is a simple English names generator using LSTM bidirectional network.

The objective of this project was to observe how adding randomness to the model at different levels (adding noise to train data, and adding controlled randomness to the text-generating module) affects the quality of the output.

At the end, I proposed some simple yet interesting metrics for the quality of the generated output.

SOURCE CODE RECOGNITION

It is a classification task. I had a dataset of source codes in as much as 19 different programming languages. The objective was rather trivial - to classify the records so that a programming language is correctly recognized. What made this task interesting was using an NLP toolbox for a source code with is not a natural language.
