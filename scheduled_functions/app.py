from chalice import Chalice, Cron
from chalicelib.calculate_avgs import calculate
from chalicelib.calculation_scheduler import schedule

app = Chalice(app_name='scheduled_functions')

@app.schedule(Cron("22,", "0,6,12,18", "*", "*", "?", "*"))
def calc_scheduler(event):
    schedule(event, calc_func_name="scheduled_functions-dev-calculate_avgs")


@app.lambda_function()
def calculate_avgs(event, context):
    calculate(event)
