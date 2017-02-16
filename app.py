import os
import requests
import operator
import re
import nltk
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup

from flask import Flask
from flask import render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        # get url that user entered
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append('Unable to get URL')
            return render_template('index.html', errors=errors)

        if r:
            # text processing
            raw = BeautifulSoup(r.text, 'html.parser').get_text()
            nltk.data.path.append('./nltk_data/')  # set path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)
            # remove punctutation, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)
            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)
            # save results
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True)[:10]
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count)
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database")
    return render_template('index.html', errors=errors, results=results)


@app.route('/<name>')
def hello_name(name):
    return "Hello {}".format(name)


if __name__ == '__main__':
    app.run()
