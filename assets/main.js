window.onload = function () {
    main()
}

function runUpdateTimeClock() {

}

function pullAndRender() {
    fetch("api/data").then(response => response.json())
        .then(data => {
            document.getElementById("dayNum").innerText = data.day;
            window.lastUpdated = data.lastUpdated;
            window.refreshTime = data.refreshTime;

            totalSorted = data.total.sort((a, b) => {
                return a.local_score > b.local_score
            })

            document.getElementById("total-table-insert").innerHTML = ""

            totalSorted.forEach((item, index) => {
                row = document.createElement("tr");
                positionEl = document.createElement("td");
                positionEl.innerText = index + 1;

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
        })
}

function main() {
    runUpdateTimeClock()
    pullAndRender()
    setInterval(pullAndRender, 5000)
}