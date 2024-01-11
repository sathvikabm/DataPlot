from flask import Flask, render_template
from flask import request
import plotly.graph_objs as go
import plotly.offline as pyo
import os
import psycopg2
from plotly.subplots import make_subplots
import csv
import io

app = Flask(__name__)


# Gets the name of all the tables, local.env credentials passed
def get_table_names():
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
    )
    cur = conn.cursor()
    query = (
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
    )
    # Query to execute to get name of all tables
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()

    table_names = [row[0] for row in results]
    return table_names[:4]


# Getting the values of x and y as array and passing it with tht particular table name
def get_table_data(table_name, start_time=None, end_time=None):
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
    )
    cur = conn.cursor()
    query = f'SELECT time, value FROM public."{table_name}"'

    if start_time and end_time:
        query += f" WHERE time >= '{start_time}' AND time <= '{end_time}'"

    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()

    time_data = []
    value_data = []

    for row in results:
        time_data.append(row[0])
        value_data.append(row[1])

    return {"table_name": table_name, "time_data": time_data, "value_data": value_data}


# for the index page
@app.route("/")
def index():
    start_time = request.args.get("start-time")
    end_time = request.args.get("end-time")
    # getting values from the form start and end time
    table_names = get_table_names()
    if table_names:
        table_names = table_names[:4]
    else:
        table_names = []
    all_data = [
        get_table_data(table_name, start_time, end_time) for table_name in table_names
    ]

    # Convert data to CSV format
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Table Name", "Time", "Value"])

    for data in all_data:
        for time, value in zip(data["time_data"], data["value_data"]):
            writer.writerow([data["table_name"], time, value])

    csv_data = output.getvalue()
    output.close()

    # dividing the pages into 4 parts
    fig = make_subplots(rows=2, cols=2)

    for index, data in enumerate(all_data):
        trace = go.Scatter(
            x=data["time_data"],
            y=data["value_data"],
            mode="lines",
            name=data["table_name"],
        )
        row, col = divmod(index, 2)
        fig.add_trace(trace, row=row + 1, col=col + 1)

    graph = pyo.plot(fig, output_type="div", include_plotlyjs="cdn")

    fig.update_layout(
        autosize=True,
        width=None,
        height=None,
        margin=dict(l=50, r=50, t=100, b=100),
    )
    # return the template as index.html graph and csv data is passed
    return render_template("index.html", graph=graph, csv_data=csv_data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8888)
