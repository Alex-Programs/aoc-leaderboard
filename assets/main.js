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

            data.total.forEach((item, index) => {
                row = document.createElement("tr");
                positionEl = document.createElement("td");
                positionEl.innerText = index + 1;

                // TODO continue this. Remember, points are easy,
                // it's the total leaderboard
            })
        })
}

function main() {
    runUpdateTimeClock()
    pullAndRender()
    setInterval(pullAndRender, 5000)
}