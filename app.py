from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def input_data():
    return render_template('input.html')


@app.route('/safety')
def safety():
    #pull in data from the form on the input.html page
    starting_location = request.args.get('starting_location')
    weather = request.args.get('weather')

    the_route_in = starting_location + " " + weather

    #In the future, pull in the input data and plug it into the model here...
    
    
    return render_template("output.html", the_route = the_route_in)


if __name__ == "__main__":
    app.run(debug=True)