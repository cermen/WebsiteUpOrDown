from flask import Flask, render_template, redirect, request, send_file
from requests import head
from requests.exceptions import ConnectionError, MissingSchema
import pandas as pd

app = Flask(__name__)


def url_is_up(url):
    try:
        return True if head(url).status_code // 100 in [2, 3] else False
    except ConnectionError:
        return False


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/check', methods=['GET', 'POST'])
def check():
    if request.method == 'POST':
        url = request.form['url']

        try:
            up_down = '가능' if url_is_up(url) else '불가능'
        except MissingSchema:
            return redirect('/')
        else:
            return render_template('result.html', url=url, result=up_down)


@app.route('/', methods=['GET', 'POST'])
def multi_check():
    if request.method == 'POST':
        file = request.files['check_file']
        try:
            file.save(file.filename)
        except FileNotFoundError:
            return redirect('/')
        else:
            name, ext = file.filename.split('.')
            if ext in ['xls', 'xlsx']:
                file = pd.read_excel(file.filename)
                file.to_csv(name + '.csv', encoding='cp949')
            else:
                file = pd.read_csv(file.filename, encoding='cp949')

            file.dropna(axis=0, inplace=True, how='all')
            file.dropna(axis=1, inplace=True, how='all')

            if file.columns.str.contains('Unnamed').all():
                file = file.transpose()
                file.set_index(file.columns[0], inplace=True)
                file = file.transpose()

            file['접속 가능 여부'] = file.iloc[:, -1].apply(lambda url: 'O' if url_is_up(url) else 'X')

            file.set_index('No.', inplace=True)

            new_filename = name + '_검사 결과.csv'
            file.to_csv(new_filename, mode='w', encoding='cp949')

            return send_file(new_filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
