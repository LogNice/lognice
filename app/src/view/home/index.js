window.onload = () => {
    const create = document.querySelector('#create')
    const join = document.querySelector('#join')
    const summary = document.querySelector('#summary')

    create.onclick = () => {
        location.href = '/create'
    }

    join.onclick = () => {
        bootbox.prompt('Enter session id:', sessionId => {
            if (sessionId) {
                location.href = `/submit?session-id=${sessionId}`
            }
        })
    }

    summary.onclick = () => {
        bootbox.prompt('Enter session id:', sessionId => {
            if (sessionId) {
                location.href = `/summary?session-id=${sessionId}`
            }
        })
    }
}
