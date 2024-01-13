# dash-clinical-analytics

## About this app
The application was reengineered using the Polars library and Dash AG Grid. Additionally, several enhancements were incorporated, such as the inclusion of a button for applying filters and the implementation of a loading mechanism for the charts.

## Requirements

* Python 3

## How to run this app

We suggest you to create a virtual environment for running this app with Python 3. Clone this repository 
and open your terminal/command prompt in the root folder.

```
git clone https://github.com/adsribeiro/dash-clinical-analytics
python3 -m virtualenv venv

```
In Unix system:
```
source venv/bin/activate

```
In Windows: 

```
venv\Scripts\activate
```

Install all required packages by running:
```
pip install -r requirements.txt
```

Run this app locally with:
```
python app.py
```

## Screenshot

![screenshot](img/screencapture.png)

## Resources

* [Dash](https://dash.plot.ly/)
* Inspired by [Dash Gallery]([https://dash.gallery/dash-clinical-analytics/]).
