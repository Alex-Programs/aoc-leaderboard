window.onload = function () {
    main()
}

window.lastPull = 0;

function runUpdateTimeClock() {
    setInterval(() => {
        const timeSince = Math.floor((Date.now() / 1000) - window.lastUpdated)
        const timeUntil = window.refreshTime - timeSince

        if (timeUntil < 1) {
            document.getElementById("timeUntilUpdate").innerText = "Updating..."
            pullAndRender()
            return
        }

        document.getElementById("timeUntilUpdate").innerText = "Updating in " + secondsToTime(timeUntil)
    }, 500)
}

function secondsToTime(secs) {
    let days = Math.floor(secs / (3600 * 24));
    let hours = Math.floor(secs / 3600)
    let minutes = Math.floor((secs - (hours * 3600)) / 60)
    let seconds = secs - (hours * 3600) - (minutes * 60)

    if (hours < 100) {
        return hours.toString().padStart(2, "0") + ":" + minutes.toString().padStart(2, "0") + ":" + seconds.toString().padStart(2, "0")
    } else {
        return days.toString().padStart(2, "0") + " days"
    }
}

function pullAndRender() {
    if (window.lastPull > (Date.now() / 1000) - 1) {
        console.log(window.lastPull, (Date.now() / 1000) - 1, window.lastPull - (Date.now() / 1000) - 1)
        return
    }

    window.lastPull = Date.now() / 1000

    fetch("api/data").then(response => response.json())
        .then(data => {
            if (data.reload) {
                location.reload()
                return
            }
            if (data.day === "INVALID") {
                window.location.replace("countdown.html")
            }

            document.getElementById("dayNum").innerText = data.day;
            window.lastUpdated = data.lastUpdated;
            window.refreshTime = data.refreshTime;

            // Render total leaderboard

            totalSorted = data.total.sort((a, b) => {
                if (a.local_score < b.local_score) {
                    return 1
                }

                if (a.local_score == b.local_score) {
                    return a.name > b.name ? 1 : -1
                }

                return -1
            })

            document.getElementById("total-table-insert").innerHTML = ""

            totalSorted.forEach((item, index) => {
                // Stop if last element lower than 75% of the screen
                const childrenEls = document.getElementById("total-table-insert").children
                if (childrenEls.length > 5) {
                    const lastChild = childrenEls[childrenEls.length - 1]
                    const lastChildBottom = lastChild.getBoundingClientRect().bottom
                    const screenBottom = window.innerHeight
                    if (lastChildBottom > screenBottom * 0.8) {
                        return
                    }
                }

                row = document.createElement("tr");
                positionEl = document.createElement("td");
                positionEl.innerText = index;

                pointsEl = document.createElement("td")
                pointsEl.innerText = item.local_score

                nameEl = document.createElement("td")
                nameEl.innerText = item.name

                starsEl = document.createElement("td")
                starsEl.innerText = item.stars

                row.appendChild(positionEl)
                row.appendChild(pointsEl)
                row.appendChild(nameEl)
                row.appendChild(starsEl)

                document.getElementById("total-table-insert").appendChild(row)
            })

            // Render daily leaderboard
            daySorted = data.today.sort((a, b) => {
                if (a.points < b.points) {
                    return 1
                }

                if (a.points == b.points) {
                    return a.name > b.name ? 1 : -1
                }

                return -1
            })

            document.getElementById("day-table-insert").innerHTML = ""
            daySorted.forEach((item, index) => {
                // Stop if last element lower than 75% of the screen
                const childrenEls = document.getElementById("day-table-insert").children
                if (childrenEls.length > 5) {
                    const lastChild = childrenEls[childrenEls.length - 1]
                    const lastChildBottom = lastChild.getBoundingClientRect().bottom
                    const screenBottom = window.innerHeight
                    if (lastChildBottom > screenBottom * 0.8) {
                        return
                    }
                }
                row = document.createElement("tr");
                positionEl = document.createElement("td");
                positionEl.innerText = index;

                pointsEl = document.createElement("td")
                pointsEl.innerText = Math.floor(item.points)

                nameEl = document.createElement("td")
                nameEl.innerText = item.name

                if (item.star1_time) {
                    starsOEl = document.createElement("td")
                    starsOEl.innerText = secondsToTime(item.star1_time + (4 * 60 * 60))
                } else {
                    starsOEl = document.createElement("td")
                    starsOEl.innerText = "N/A"
                }

                if (item.star2_time) {
                    starsTEl = document.createElement("td")
                    starsTEl.innerText = secondsToTime(item.star2_time + (4 * 60 * 60))
                } else {
                    starsTEl = document.createElement("td")
                    starsTEl.innerText = "N/A"
                }

                row.appendChild(positionEl)
                row.appendChild(pointsEl)
                row.appendChild(nameEl)
                row.appendChild(starsOEl)
                row.appendChild(starsTEl)

                document.getElementById("day-table-insert").appendChild(row)
            })
        })
}

function main() {
    runUpdateTimeClock()
    pullAndRender()
    setInterval(pullAndRender, 5000)
}