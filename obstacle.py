import itertools


class Obstacle():
    id_iter = itertools.count()

    def __init__(self, x1, x2, frame, yaw, area):

        self.id = next(self.id_iter)

        height, width, _ = frame.shape

        # Angle a to angle b,
        # Basically where the object starts and finishes from the drones point of view using its yaw
        # and where the object is in the frame.
        self.a, self.b = calculate_range(x1, x2, yaw, width)

        self.visited = False
        self.area = area

    def get_range(self):
        return self.a, self.b

    def get_center(self):
        return (self.a + self.b) / 2

    def update(self, x1, x2, yaw, frame, area):
        height, width, _ = frame.shape

        self.area = area
        self.a, self.b = calculate_range(x1, x2, yaw, width)

    def __str__(self):
        return "id:%s a:%s b:%s area:%s" % (self.id, self.a, self.b, self.area)


def calculate_range(x1, x2, yaw, width):
    percentage_a = x1 / width
    percentage_b = x2 / width

    # Approximate field of view (in degrees) of the drones camera in relation to its yaw.
    approx_fov = 60

    # If it is past the halfway point, or before it
    if percentage_a < 0.5:
        a = yaw - ((0.5 - percentage_a) * approx_fov)
    else:
        a = yaw + ((percentage_a - 0.5) * approx_fov)

    if percentage_b < 0.5:
        b = yaw - ((0.5 - percentage_b) * approx_fov)
    else:
        b = yaw + ((percentage_b - 0.5) * approx_fov)

    # Basically gives an approximate range of where the obstacle lies in the drones 360 degree radius
    return a, b




