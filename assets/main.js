window.onload = function () {
    main()
}

function runUpdateTimeClock() {

}

function secondsToTime(secs) {
    let days = Math.floor(secs / (3600 * 24));
    let hours = Math.floor(secs / 3600)
    let minutes = Math.floor((secs - (hours * 3600)) / 60)
    let seconds = secs - (hours * 3600) - (minutes * 60)

    if (hours < 100) {
        return hours.toString().padStart(2, "0") + ":" + minutes.toString().padEnd(2, "0") + ":" + seconds.toString().padStart(2, "0")
    } else {
        return days.toString().padStart(2, "0") + " days"
    }
}

function pullAndRender() {
    fetch("api/data").then(response => response.json())
        .then(data => {
            // TODO check if day is "INVALID", if so redirect to countdown

            document.getElementById("dayNum").innerText = data.day;
            window.lastUpdated = data.lastUpdated;
            window.refreshTime = data.refreshTime;

            // Render total leaderboard

            totalSorted = data.total.sort((a, b) => {
                return a.local_score < b.local_score
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
                return a.points < b.points
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

                starsOEl = document.createElement("td")
                starsOEl.innerText = secondsToTime(item.star1_time)

                starsTEl = document.createElement("td")
                starsTEl.innerText = secondsToTime(item.star2_time)

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