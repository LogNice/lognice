function showPlot(summary) {
    const pairs = Object.entries(summary).sort((a, b) => {
        return (a[1].time.value > b[1].time.value) ? 1 : -1
    })
    const times = pairs.map(p => p[1].time.value)
    const names = pairs.map(p => p[0])

    const trace1 = {
        type: 'bar',
        x: names,
        y: times,
        text: times.map(String),
        hoverinfo: 'none',
        textposition: 'auto',
        marker: {
            color: '#9ecae1',
            opacity: 0.6,
            line: {
                color: '#08306b',
                width: 1.5
            }
        }
    }

    const data = [trace1]

    const layout = {
        font: {
            size: 18
        },
        xaxis: {
            tickangle: -45
        }
    }

    const config = {
        responsive: true
    }

    Plotly.newPlot('summary-plot', data, layout, config)
}

window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search)
    if (!urlParams.has('session-id')) {
        window.location.replace('/notfound')
    }
    const sessionId = urlParams.get('session-id')

    const title = document.getElementById('summary-title')
    title.innerText = `[${sessionId}] Ranking`

    $.ajax({
        url: `/api/summary/${sessionId}`,
        method: 'GET',
        contentType: false,
        processData: false,
        success: res => {
            const summary = JSON.parse(res).result.summary
            showPlot(summary)
        },
        error: e => {
            const message = JSON.parse(e.responseText).message
            console.log(message)
        }
    })
}
