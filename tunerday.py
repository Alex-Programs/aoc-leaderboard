import matplotlib.pyplot as plt
import math


def score(star_time_hours):
    if star_time_hours < 9.081 * 2:
        return ((-(1 / 2) * star_time_hours) + 35) * 10

    return (100 / math.sqrt(star_time_hours)) * 11.005


def plot_score():
    xAxis = [x / 60 for x in range(0, 96 * 60)]
    yAxis = [score(x) for x in xAxis]
    plt.plot(xAxis, yAxis)

    plt.savefig("tunerday.png")


if __name__ == "__main__":
    plot_score()