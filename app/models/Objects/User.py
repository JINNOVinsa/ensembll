class User:

    def __init__(self, id_, firstname, lastname, email, hierarchical_level, plates, parentEntity, status=None, contracts=None, user_groups=None, limited_period=None, has_limited_geographical_access=None, customized_periods=None, bookings=None):
        self.id_ = id_
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.hierarchical_level = hierarchical_level
        self.status = status
        self.parentEntity = parentEntity
        self.plates = plates
        self.contracts = contracts
        self.user_groups = user_groups
        self.limited_period = limited_period
        self.has_limited_geograhical_access = has_limited_geographical_access
        self.customized_periods = customized_periods

        self.bookings = bookings

    def __str__(self):
        return f"User ({self.id_}) / name:{self.lastname} {self.firstname} / mail: {self.email} / hierarchical_level: {self.hierarchical_level} / plates: {self.plates}"
