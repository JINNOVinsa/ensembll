class Booking:

    def __init__(self, id_, userId, present, startTimestamp, endTimestamp) -> None:
        self.id_ = id_
        self.userId = userId
        self.present = present
        self.startTimeStamp = startTimestamp
        self.endTimestamp = endTimestamp
