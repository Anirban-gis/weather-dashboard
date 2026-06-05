// ======================================================
// CONFIG
// ======================================================

const API = "http://127.0.0.1:5000";

let tempChart = null;
let humidityChart = null;

let weatherMarkers = [];

// ======================================================
// LEAFLET MAP
// ======================================================

const map = L.map("map").setView(
    [22.5, 80.0],
    5
);

L.tileLayer(
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 18,
        attribution:
            "&copy; OpenStreetMap Contributors"
    }
).addTo(map);

// ======================================================
// TEMPERATURE COLORS
// ======================================================

function getColor(temp) {

    if (temp >= 40)
        return "red";

    if (temp >= 35)
        return "orange";

    if (temp >= 30)
        return "yellow";

    if (temp >= 25)
        return "green";

    return "blue";
}

// ======================================================
// LOAD DISTRICT LIST
// ======================================================

async function loadDistricts() {

    try {

        const response =
            await fetch(
                `${API}/api/districts`
            );

        const districts =
            await response.json();

        const select =
            document.getElementById(
                "districtSelect"
            );

        select.innerHTML = "";

        districts.forEach(district => {

            const option =
                document.createElement(
                    "option"
                );

            option.value = district;

            option.textContent = district;

            select.appendChild(option);

        });

    } catch (err) {

        console.error(
            "District Load Error:",
            err
        );
    }
}

// ======================================================
// LOAD LATEST WEATHER TABLE
// ======================================================

async function loadLatest() {

    try {

        const response =
            await fetch(
                `${API}/api/latest`
            );

        const data =
            await response.json();

        const tbody =
            document.querySelector(
                "#weatherTable tbody"
            );

        tbody.innerHTML = "";

        data.forEach(row => {

            const tr =
                document.createElement(
                    "tr"
                );

            tr.innerHTML = `

                <td>${row.district}</td>

                <td>${row.state}</td>

                <td>${row.temperature}</td>

                <td>${row.humidity}</td>

                <td>${row.pressure}</td>

                <td>${row.wind_speed}</td>

                <td>${row.weather}</td>

            `;

            tbody.appendChild(tr);

        });

    } catch (err) {

        console.error(
            "Latest Weather Error:",
            err
        );
    }
}

// ======================================================
// LOAD GIS MAP
// ======================================================

async function loadMap() {

    try {

        weatherMarkers.forEach(
            marker =>
                map.removeLayer(marker)
        );

        weatherMarkers = [];

        const weatherResponse =
            await fetch(
                `${API}/api/latest`
            );

        const weatherData =
            await weatherResponse.json();

        const locationResponse =
            await fetch(
                `${API}/api/locations`
            );

        const locations =
            await locationResponse.json();

        locations.forEach(loc => {

            const weather =
                weatherData.find(

                    x =>
                    x.district ===
                    loc.District

                );

            if (!weather)
                return;

            const marker =
                L.circleMarker(

                    [
                        loc.Latitude,
                        loc.Longitude
                    ],

                    {
                        radius: 8,

                        fillColor:
                            getColor(
                                weather.temperature
                            ),

                        color: "#000",

                        weight: 1,

                        fillOpacity: 0.8
                    }

                ).addTo(map);

            marker.bindPopup(`

                <b>${loc.District}</b>

                <br>

                ${weather.state}

                <br><br>

                Temp:
                ${weather.temperature} °C

                <br>

                Humidity:
                ${weather.humidity} %

                <br>

                Wind:
                ${weather.wind_speed}

                <br>

                Weather:
                ${weather.weather}

            `);

            marker.on(
                "click",
                () => {

                    document
                        .getElementById(
                            "districtSelect"
                        )
                        .value =
                        loc.District;

                    loadHistory();

                }
            );

            weatherMarkers.push(
                marker
            );

        });

    } catch (err) {

        console.error(
            "Map Error:",
            err
        );
    }
}

// ======================================================
// HISTORY CHARTS
// ======================================================

async function loadHistory() {

    try {

        const district =
            document.getElementById(
                "districtSelect"
            ).value;

        const response =
            await fetch(
                `${API}/api/history/${district}`
            );

        const data =
            await response.json();

        if (
            !Array.isArray(data) ||
            data.length === 0
        ) {

            alert(
                "No history found."
            );

            return;
        }

        const labels =
            data.map(
                x => x.timestamp
            );

        const temperature =
            data.map(
                x => x.temperature
            );

        const humidity =
            data.map(
                x => x.humidity
            );

        if (tempChart)
            tempChart.destroy();

        if (humidityChart)
            humidityChart.destroy();

        // ==========================
        // TEMPERATURE CHART
        // ==========================

        tempChart =
            new Chart(

                document
                .getElementById(
                    "tempChart"
                ),

                {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Temperature (°C)",

                                data:
                                    temperature,

                                borderWidth: 2
                            }

                        ]
                    },

                    options: {

                        responsive: true
                    }
                }
            );

        // ==========================
        // HUMIDITY CHART
        // ==========================

        humidityChart =
            new Chart(

                document
                .getElementById(
                    "humidityChart"
                ),

                {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Humidity (%)",

                                data:
                                    humidity,

                                borderWidth: 2
                            }

                        ]
                    },

                    options: {

                        responsive: true
                    }
                }
            );

        // ==========================
        // SUMMARY PANEL
        // ==========================

        const latest =
            data[data.length - 1];

        document
            .getElementById(
                "districtSummary"
            )
            .innerHTML = `

            <b>${district}</b>

            <br><br>

            Temperature:
            ${latest.temperature} °C

            <br>

            Humidity:
            ${latest.humidity} %

            <br>

            Pressure:
            ${latest.pressure}

            <br>

            Wind:
            ${latest.wind_speed}

            <br>

            Weather:
            ${latest.weather}

        `;

    } catch (err) {

        console.error(
            "History Error:",
            err
        );
    }
}

// ======================================================
// AUTO REFRESH
// ======================================================

function refreshDashboard() {

    loadLatest();

    loadMap();
}

// ======================================================
// INITIAL LOAD
// ======================================================

window.onload = async () => {

    await loadDistricts();

    await loadLatest();

    await loadMap();

};

// Refresh every 15 minutes

setInterval(
    refreshDashboard,
    900000
);