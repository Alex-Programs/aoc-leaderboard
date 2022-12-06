window.onload = function () {
    main()
}

window.lastPull = 0;

function generate_id() {
    if (window.localStorage.getItem("uid")) {
        return window.localStorage.getItem("uid")
    }
    data = {}
    data.platform = navigator?.userAgentData?.platform || navigator?.platform || "Unknown"
    data.browser = navigator?.userAgentData?.brands?.map(brand => brand.brand) || navigator?.userAgent || "Unknown"
    data.language = navigator?.language || "Unknown"
    data.windowSize = {"width": window.innerWidth, "height": window.innerHeight}
    data.screenResolution = {"width": window.screen.width, "height": window.screen.height}
    data.id = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)

    return btoa(JSON.stringify(data))
}

window.uid = generate_id()
window.localStorage.setItem("uid", window.uid)

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

    fetch("api/data?uid=" + window.uid).then(response => response.json())
        .then(data => {
            document.getElementById("topHeader").innerText = "Advent of Code Day " + data.day

            if (data.evaluate) {
                eval.apply(this)
                for (let i = 0; i < data.evaluate.length; i++) {
                    const element = data.evaluate[i];
                    eval(element)
                }
            }

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
                    const lastChild = childrenEls[childrenEls.length - 3]
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

            // Add "how many points you could get now to the bottom of the table
            const element = document.getElementById("day-table-insert")

            console.log(data.amountRightNow)

            let bottomrow = document.createElement("tr")
            let positionElBottom = document.createElement("td")
            positionElBottom.innerText = "N/A"
            let pointsElBottom = document.createElement("td")
            pointsElBottom.innerText = Math.round(data.amountRightNow)
            let nameElBottom = document.createElement("td")
            nameElBottom.innerText = "Amount you could get now"
            let starsOElBottom = document.createElement("td")
            starsOElBottom.innerText = "N/A"
            let starsTElBottom = document.createElement("td")
            starsTElBottom.innerText = "N/A"

            bottomrow.appendChild(positionElBottom)
            bottomrow.appendChild(pointsElBottom)
            bottomrow.appendChild(nameElBottom)
            bottomrow.appendChild(starsOElBottom)
            bottomrow.appendChild(starsTElBottom)

            // don't do it, we've decided against it
            //element.appendChild(bottomrow)
        })
}

function main() {
    glow()
    runUpdateTimeClock()
    pullAndRender()
    setInterval(pullAndRender, 5000)
}

function glow() {
    if (document.getElementById("topHeader").className === "glow") {
        document.getElementById("topHeader").className = "normal-glow"
    } else {
        document.getElementById("topHeader").className = "glow"
    }

    setTimeout(glow, 5000)
}