class Entity:
    def __init__(self, id_, nbPlacesAllocated, nbFreePlaces) -> None:
        self.id_ = id_
        self.nbPlacesAllocated = nbPlacesAllocated
        self.nbFreePlaces = nbFreePlaces

    def __str__(self):
        return f"Entity ({self.id_}) / capacity: {self.nbPlacesAllocated} / free: {self.nbFreePlaces}"
