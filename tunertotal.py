import matplotlib.pyplot as plt
import math


def score(star_time_hours):
    if star_time_hours <= 24:
        return (((-(1/4)) * star_time_hours) + 100)

    return ((1 / math.sqrt(star_time_hours)) * 460)


def plot_score():
    xAxis = [x / 60 for x in range(0, 96 * 60)]
    yAxis = [score(x) for x in xAxis]
    plt.plot(xAxis, yAxis)

    plt.show()


if __name__ == "__main__":
    plot_score()