function showPlot(summary, topN) {
    const pairs = Object.entries(summary).sort((a, b) => {
        return (a[1].time.value > b[1].time.value) ? 1 : -1
    }).slice(0, topN)
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
        },
        yaxis: {
            title: {
                text: 'CPU Time (us)',
                font: {
                    size: 15
                }
            }
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
    const topN = 20

    const title = document.getElementById('summary-title')
    title.innerText = `[${sessionId}] Ranking - Top ${topN}`

    $.ajax({
        url: `/api/summary/${sessionId}`,
        method: 'GET',
        contentType: false,
        processData: false,
        success: res => {
            const summary = JSON.parse(res).result.summary
            showPlot(summary, topN)
        },
        error: e => {
            const message = JSON.parse(e.responseText).message
            console.log(message)
        }
    })

    $.ajax({
        url: `/api/summary/table/${sessionId}`,
        method: 'GET',
        contentType: false,
        processData: false,
        success: res => {
            const summary = JSON.parse(res).result.summary_str
            const table = document.getElementById('summary-table')
            table.innerHTML = `<pre>${summary}</pre>`
        },
        error: e => {
            const message = JSON.parse(e.responseText).message
            console.log(message)
        }
    })
}
