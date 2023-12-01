window.onload = function () {
    main()
}

window.lastPull = 0;

window.row_limit = 30;

window.show_with_no_stars = true;

//window.pre_announce_leaderboard = ['2318292', '2332860', '2360231', '2537910', '2490681', '2393969', '1526672', '2796106', '809157', '2217068', '2490400', '2322145', '3210419', '2805401', '2322139', '2494040', '662519', '2257223', '2769410', '2494015', '2394117', '2502187', '2335991', '2360127', '2322914']

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

function format_num(number) {
    // Turn:
    // 1 -> 1
    // 10 -> 10
    // 100 -> 100
    // 1000 -> 1000
    // 10000 -> 10 000
    // 100000 -> 100 000
    // 1000000 -> 1 000 000

    // If the number is less than or equal to 1000, return it as is
    if (number < 10000) {
        return number.toString();
    }

    // Otherwise, insert spaces every three digits from the right
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function secondsToSmallTime(secs) {
    let days = Math.floor(secs / (3600 * 24));
    let hours = Math.floor(secs / 3600)
    let minutes = Math.floor(secs/ 60)
    let seconds = secs

    if (seconds < 180) {
        return seconds.toString().padStart(2, "0") + "s"
    }

    if (minutes < 180) {
        return minutes.toString().padStart(2, "0") + "m"
    }

    return hours.toString().padStart(2, "0") + "h"
}

function secondsToTime(secs) {
    let days = Math.floor(secs / (3600 * 24));
    let hours = Math.floor(secs / 3600)
    let minutes = Math.floor((secs - (hours * 3600)) / 60)
    let seconds = secs - (hours * 3600) - (minutes * 60)

    if (hours < 1) {
        return "00:" + minutes.toString().padStart(2, "0") + ":" + seconds.toString().padStart(2, "0")
    }

    if (hours < 100) {
        return hours.toString().padStart(2, "0") + ":" + minutes.toString().padStart(2, "0")
    }
    
    return days.toString() + " days"
}

function pullAndRender() {
    if (window.lastPull > (Date.now() / 1000) - 1) {
        console.log("NOT PULLING")
        console.log(window.lastPull, (Date.now() / 1000) - 1, window.lastPull - (Date.now() / 1000) - 1)
        return
    }

    window.lastPull = Date.now() / 1000
    let cachebust = Math.random().toString(36).substring(2, 15)

    fetch("api/data?uid=" + window.uid + "&cachebust=" + cachebust).then(response => response.json())
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
                    return a.name.localeCompare(b.name)
                }

                return -1
            })

            document.getElementById("total-table-insert").innerHTML = ""

            totalSorted.forEach((item, index) => {
                if (index > window.row_limit) {
                    return;
                }

                if ((!window.show_with_no_stars) && item.stars == 0) {
                    return;
                }

                row = document.createElement("tr");
                positionEl = document.createElement("td");
                positionEl.innerText = index;

                pointsEl = document.createElement("td")
                pointsEl.innerText = format_num(item.local_score)

                nameEl = document.createElement("td")
                nameEl.innerText = item.name

                starsEl = document.createElement("td")
                starsEl.innerText = item.stars
                console.log(item)

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
                if (index > window.row_limit) {
                    return;
                }

                row = document.createElement("tr");
                positionEl = document.createElement("td");
                positionEl.innerText = index;

                pointsEl = document.createElement("td")
                pointsEl.innerText = format_num(Math.floor(item.points))

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
                    deltaTime = item.star2_time - item.star1_time
                    deltaTimeText = secondsToSmallTime(deltaTime)
                } else {
                    starsTEl = document.createElement("td")
                    starsTEl.innerText = "N/A"
                    deltaTimeText = "N/A"
                }

                deltaEl = document.createElement("td")
                deltaEl.innerText = deltaTimeText

                row.appendChild(positionEl)
                row.appendChild(pointsEl)
                row.appendChild(nameEl)
                row.appendChild(starsOEl)
                row.appendChild(starsTEl)
                row.appendChild(deltaEl)

                document.getElementById("day-table-insert").appendChild(row)
            })
        })
}

function main() {
    runUpdateTimeClock()
    pullAndRender()
    setInterval(pullAndRender, 10000)
}