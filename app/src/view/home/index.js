window.onload = () => {
    const create = document.querySelector('#create')
    const join = document.querySelector('#join')

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
}
