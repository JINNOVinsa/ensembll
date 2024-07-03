BASE_URL = "https://cerberus.parkki.io/v1.0.0"

# ------- GET URLs -------

GET_TOKEN = "/auth/login"

GET_REFRESH_TOKEN = "/auth/request_access_token"

GET_CONTRACTS = "/contracts"

GET_USER_GROUPS = "/user_groups"

GET_USERS = "/users"

GET_USER_FROM_ID = "/users/{id}"

GET_USER_SELF = "/users/me"

GET_ACCESSES = "/accesses"

GET_ACCESS = "/accesses/{id}"

GET_PARKINGS = "/parkings"

GET_PARKING = "/parkings/{id}"

# ------- POST URLs -------
POST_AUTH = "/auth/login"

POST_USER_GROUP = "/user_groups"

POST_USER = "/users"

POST_SET_PSWD = "/users/password"

POST_RESET_PSWD = "/users/reset_password"

POST_OPEN_ACCESS = "/accesses/{id}/open"

POST_FORCE_OPEN_ACCESS = "/accesses/{id}/open/force"

POST_PERIOD = "/periods"

# ------- PUT URLs -------
PUT_USER = "/users/{id}"

# ------- DELETE URLs -------

DELETE_USER = "/users/{id}"

DELETE_PERIOD = "/periods/{id}"