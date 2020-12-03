window.onload = () => {
    const create = document.querySelector('#create')
    const join = document.querySelector('#join')

    create.onclick = () => {
        location.href = '/create'
    }

    join.onclick = () => {
        location.href = '/join'
    }
}
