# importing libraries
import os
import numpy as np
import pandas as pd
import flask
import pickle
from flask import Flask, render_template, request
# creating instance of the class
app = Flask(__name__)
# to tell flask what url shoud trigger the function index()
@app.route('/')
@app.route('/authorization')
def authorization():
    return flask.render_template('authorization.html')

@app.route('/access', methods=['GET', 'POST'])
def access():
    if request.method == 'POST':
        to_access_list = request.form.to_dict()
        to_access_list = list(to_access_list.values())
        if to_access_list[0] == 'Admin' and to_access_list[1] == 'Admin':
            return render_template("access_is_open.html", access='Доступ открыт')
        else:
            return render_template("access_closed.html", access='Доступ закрыт')
print(access)
@app.route('/index')
def index():
    return flask.render_template('cc_fraud.html')


# prediction function
def ValuePredictor(to_predict_list):
    clm = ['cc_freq', 'cc_freq_class', 'city', 'job', 'age', 'gender', 'merchant',
           'category', 'distance_km', 'month', 'day', 'hour',
           'hours_diff_bet_trans', 'amt']

    to_predict = pd.DataFrame(np.array(to_predict_list).reshape(1, 14), columns = clm)
    loaded_model = pickle.load(open("model_rf.pkl", "rb"))
    result = loaded_model.predict(to_predict)
    probability = loaded_model.predict_proba(to_predict)
    return result[0], probability


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        for i in range(len(to_predict_list)):
            if to_predict_list[i].isdigit():
                to_predict_list[i] = int(to_predict_list[i])
        if to_predict_list[0] <= 1000:
            to_predict_list.insert(1, 1)
        elif 1000 < to_predict_list[0] <= 2000:
            to_predict_list.insert(1, 2)
        elif 2000 < to_predict_list[0] <= 3000:
            to_predict_list.insert(1, 3)
        elif 3000 < to_predict_list[0] <= 4000:
            to_predict_list.insert(1, 4)
        elif 4000 < to_predict_list[0] <= 5000:
            to_predict_list.insert(1, 5)
        else:
            to_predict_list.insert(1, 6)
        result, probability = ValuePredictor(to_predict_list)

        probability_0 = probability[0][0]
        probability_1 = probability[0][1]

        if int(result) == 1:
            prediction = f'Транзакция является мошеннической с вероятностью {round(probability_1, 3)}'
        else:
            prediction = f'Транзакция не является мошеннической с вероятностью {round(probability_0, 3)}'

        return render_template("result.html", prediction=prediction)


if __name__ == "__main__":
    app.run(debug=True)