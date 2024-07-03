BASE_URL = "https://client.parkki.io/v2.4"

# ------- GET URLs -------

GET_TOKEN = "/auth/app"

GET_REFRESH_TOKEN = "/auth/request_access_token"

GET_CONTRACTS = "/apps/contracts"

GET_CONTRACT = "/apps/contract"

GET_SITES = "/apps/sites"

GET_AREAS = "/areas"

GET_GENERAL_STATS_OF_PARKING = "/areas/park/stats/general"

GET_GENERAL_STATS_OF_AREA = "/flows/stats/area/{id}"        # FORBIDDEN - NECESSARY flows.stats.area.id - parkusage

GET_DAILY_ATTENDANCE = "/areas/park/stats/daily_attendance" # FORBIDDEN - NECESSARY areas.park.stats.daily_attendance 

GET_DATA_ATTENDANCE = "/flows/stats/area/{id}/graph/attendance" # FORBIDDENT - fillrate and realfillrate

GET_AVAILABLE_PARKING = "/areas/park/data/available_parking"

GET_PARKED_CARS = "/areas/park/data/parked_cars"