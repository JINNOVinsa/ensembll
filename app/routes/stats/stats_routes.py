
import models.database.queries as db_requests

from datetime import datetime, timedelta, date
from models.api import statsUrls
from flask import request, make_response, jsonify, Blueprint, current_app
import calendar
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
from re import match

db = current_app.config['DB_APP']
db_flow = current_app.config['DB_FLOW']
mail_host = current_app.config['MAIL_HOST']
mail_pswd = current_app.config['MAIL_PSWD']
api = current_app.config['API']
contract = current_app.config['CONTRACT']
capacity = current_app.config['CAPACITY']
parked_cars = current_app.config['PARKED_CARS']
statsApi = current_app.config['STATS_API']
area_id = current_app.config['AREA_ID']

imagePath = "static/assets/park7_logo.png"

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

@stats_bp.route('/fillrate/hourly', methods=['GET'])
def get_fillrate_stats_hourly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    from_timestamp = int(from_timestamp)
    to_timestamp = int(to_timestamp)
    delta = to_timestamp - from_timestamp

    if delta <= 0:
        return make_response("BAD REQUEST", 400)

    n_hours = delta // 3600

    from_date = datetime.fromtimestamp(int(from_timestamp))

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    labels = []
    for _ in range(n_hours):
        labels.append(days[from_date.weekday()] + " " + str(from_date.hour) + "h")
        from_date = from_date + timedelta(hours=1)
    
    data = []
    for i in range(n_hours)[::24]:
        r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp+i*3600, 'to': to_timestamp-(n_hours-i-24+1)*3600, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'HOUR'})
        if (r.status_code != 200):
            return make_response("API ERROR", 500)
        
        data += list(r.json()['real_time'].values())


    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/fillrate/daily', methods=['GET'])
def get_fillrate_stats_daily():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    n_days = (int(to_timestamp) - int(from_timestamp)) // 86400

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(int(from_timestamp))
    labels = []
    for _ in range(n_days):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(days=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})
    
    if (r.status_code != 200):
        return make_response("API ERROR", 500)

    return make_response(jsonify({'data': list(r.json()['real_time'].values()), 'labels': labels}), 200)

@stats_bp.route('/fillrate/weekly', methods=['GET'])
def get_fillrate_stats_weekly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    n_weeks = (int(to_timestamp) - int(from_timestamp)) // 604800

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(int(from_timestamp))
    labels = []
    for _ in range(n_weeks):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(weeks=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    week_sum = 0
    values = list(r.json()['real_time'].values())
    data = []
    for i in range(len(values)):
        if i%7 == 0 and i != 0:
            data.append(week_sum)
            week_sum = 0

        week_sum += values[i]

    data.append(week_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/fillrate/monthly', methods=['GET'])
def get_fillrate_stats_monthly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    n_months = (int(to_timestamp) - int(from_timestamp)) // 2592000

    months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    from_date = datetime.fromtimestamp(int(from_timestamp))
    data = []
    labels = []
    value_index_offset = 0
    values = list(r.json()['real_time'].values())
    for _ in range(n_months):
        end_month_day = calendar.monthrange(from_date.year, from_date.month)[1]

        labels.append(months[from_date.month-1])
        from_date = from_date + timedelta(days=end_month_day)
        month_sum = 0
        for v in values[value_index_offset:value_index_offset+end_month_day]:
            month_sum += v
        value_index_offset += end_month_day
        data.append(month_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/parkusage', methods=['GET'])
def get_parkusage_stats():
    today = date.today()
    incrementalDateStart = date(today.year-1, today.month, 1)
    incrementalDateEnd = date(today.year-1, today.month, calendar.monthrange(today.year-1, today.month)[1])
    
    startTS = datetime.combine(incrementalDateStart, datetime.min.time())
    endTS = datetime.combine(incrementalDateEnd, datetime.min.time())
    
    data = []
    for _ in range(12):
        end_month_day = calendar.monthrange(startTS.year, startTS.month)[1]
        
        r = statsApi.get_api(statsUrls.GET_GENERAL_STATS_OF_AREA, path_parameters={'id': area_id}, query_payload={'from':startTS.timestamp(), 'to':endTS.timestamp(), 'flow_types':'CAR,TWO_WHEELER,DELIVERY'})
        if r.status_code != 200:
            return make_response("API ERROR", 500)
        
        data.append(r.json()['flow']['in']['value'])

        startTS = startTS + timedelta(days=end_month_day)
        endTS = endTS + timedelta(days=end_month_day)


    months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    labels = months[date.today().month - 1::] + months[:date.today().month - 1]

    
    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/realfillrate/hourly', methods=['GET'])
def get_realfillrate_stats_hourly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    from_timestamp = int(from_timestamp)
    to_timestamp = int(to_timestamp)

    n_hours = (to_timestamp - from_timestamp) // 3600

    from_date = datetime.fromtimestamp(int(from_timestamp))

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    labels = []
    for _ in range(n_hours):
        labels.append(days[from_date.weekday()] + " " + str(from_date.hour) + "h")
        from_date = from_date + timedelta(hours=1)

    data = []
    for i in range(n_hours)[::24]:
        r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp+i*3600, 'to': to_timestamp-(n_hours-i-24+1)*3600, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'HOUR'})
        if (r.status_code != 200):
            return make_response("API ERROR", 500)
        r_data = r.json()
        data += [v1/v2 if v2 != 0 and not (v1 is None or v2 is None) else 0 for v1, v2 in zip(list(r_data['real_time'].values()), list(r_data['previsional'].values()))]

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/realfillrate/daily', methods=['GET'])
def get_realfillrate_stats_daily():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    from_timestamp = int(from_timestamp)
    to_timestamp = int(to_timestamp)
    delta = to_timestamp - from_timestamp

    if delta <= 0:
        return make_response("BAD REQUEST", 400)

    n_days = delta // 86400

    from_date = datetime.fromtimestamp(from_timestamp)

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(from_timestamp)
    labels = []
    for _ in range(n_days):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(days=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})
    
    if (r.status_code != 200):
        return make_response("API ERROR", 500)

    data = [v1/v2 is not(v1 is None or v2 is None) for v1, v2 in zip(list(r.json()['real_time'].values()), list(r.json()['previsional'].values()))]
    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/realfillrate/weekly', methods=['GET'])
def get_realfillrate_stats_weekly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    n_weeks = (int(to_timestamp) - int(from_timestamp)) // 604800

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(int(from_timestamp))
    labels = []
    for _ in range(n_weeks):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(weeks=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    week_sum = 0
    values = list(r.json()['real_time'].values())
    previsional = list(r.json()['previsional'].values())
    data = []
    for i in range(len(values)):
        if i%7 == 0 and i != 0:
            data.append(week_sum)
            week_sum = 0

        if not(values[i] is None or previsional[i] is None):
            week_sum += values[i]/previsional[i]

    data.append(week_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/realfillrate/monthly', methods=['GET'])
def get_realfillrate_stats_monthly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    n_months = (int(to_timestamp) - int(from_timestamp)) // 2592000

    months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    from_date = datetime.fromtimestamp(int(from_timestamp))
    data = []
    labels = []
    value_index_offset = 0
    values = list(r.json()['real_time'].values())
    previsional = list(r.json()['previsional'].values())
    for _ in range(n_months):
        end_month_day = calendar.monthrange(from_date.year, from_date.month)[1]

        labels.append(months[from_date.month-1])
        from_date = from_date + timedelta(days=end_month_day)
        month_sum = 0
        for v, p in zip(values[value_index_offset:value_index_offset+end_month_day], previsional[value_index_offset:value_index_offset+end_month_day]):
            month_sum += v/p
        value_index_offset += end_month_day
        data.append(month_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@stats_bp.route('/parkduration/plate', methods=['GET'])
def get_parkduration_plate():
    plate = request.args.get('plate', default=None)

    if plate is None or (not match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) and not match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate)):
        return make_response("BAD REQUEST", 400)
    
    records_in = db_flow.read(db_requests.GET_PLATE_IN_DATETIMES_RECORDS.format(plate=plate))
    records_out = db_flow.read(db_requests.GET_PLATE_OUT_DATETIMES_RECORDS.format(plate=plate))

    payload = {}

    duration = timedelta(days=0)
    for i in range(min(len(records_in), len(records_out))):
        duration += records_out[i][1] - records_in[i][1]
    
    present = len(records_in) == len(records_out)+1

    payload["duration"] = {
                "days": duration.days,
                "hours": duration.seconds//3600,
                "minutes": duration.seconds//60%60
                }
    
    payload["present"] = present

    ongoing_duration = None
    if present:
        ongoing_duration = datetime.now() - records_in[-1][1]
        print(ongoing_duration)

        payload["ongoing"] = {
                "days": ongoing_duration.days,
                "hours": ongoing_duration.seconds//3600,
                "minutes": ongoing_duration.seconds//60%60
                }

    return make_response(jsonify(payload), 200)

@stats_bp.route('/parkduration/entity', methods=['GET'])
def get_parkduration_entity():
    entity = request.args.get('entity', default=None)

    if entity is None:
        return make_response("BAD REQUEST", 400)

    # Get entity's plates
    plates = db.read(db_requests.GET_PLATES_FROM_ENTITY.format(entityId=str(entity)))

    # Remove duplicates
    plates = [p[0] for p in set(plates)]

    duration = timedelta(days=0)

    for plate in plates:
        records_in = db_flow.read(db_requests.GET_PLATE_IN_DATETIMES_RECORDS.format(plate=plate))
        records_out = db_flow.read(db_requests.GET_PLATE_OUT_DATETIMES_RECORDS.format(plate=plate))


        for i in range(min(len(records_in), len(records_out))):
            duration += records_out[i][1] - records_in[i][1]

    return make_response({"duration": {
                    "days": duration.days,
                    "hours": duration.seconds//3600,
                    "minutes": duration.seconds/60%60
                }
            }, 200)