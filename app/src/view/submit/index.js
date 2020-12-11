function isEmptyOrSpaces(str){
    return str === null || str.match(/^ *$/) !== null
}

window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search)
    if (!urlParams.has('session-id')) {
        window.location.replace('/notfound')
    }
    const sessionId = urlParams.get('session-id')

    const highlight = editor => {
        editor.textContent = editor.textContent
        hljs.highlightBlock(editor)
    }
    const options = {
        tab: ' '.repeat(4),
        indentOn: /[({:\[]$/,
    }
    const jar = CodeJar(document.querySelector('#editor'), withLineNumbers(highlight), options)
    jar.updateCode(
`# 'Solution' class is mandatory
class Solution:
    # so is the 'solve' method
    def solve(self, **kwargs):
        pass`
    )

    const submit = document.querySelector('#submit')
    const status = document.querySelector('#status')
    const username = document.querySelector('#username')

    $.ajax({
        url: `/api/description/${sessionId}`,
        method: 'GET',
        contentType: false,
        processData: false,
        success: res => {
            const description = JSON.parse(res).result.description
            const html = window.markdownit().render(description)
            document.getElementById('description').innerHTML = html
        },
        error: e => {
            const message = JSON.parse(e.responseText).message
            console.log(message)
        }
    })

    submit.onclick = () => {
        const name = username.value
        if (isEmptyOrSpaces(name)) {
            status.innerHTML = `<span style='color: red;'>Username cannot be empty.</span>`
            return
        }

        status.innerHTML = ''
        submit.disabled = true

        const formData = new FormData()
        formData.append('solution', new File([jar.toString()], 'solution.py'))
        formData.append('username', name)

        const previousToken = localStorage.getItem(`lognice-token-${sessionId}-${name}`)
        if (previousToken) {
            formData.append('token', previousToken)
        }

        status.innerText = 'Connecting...'

        const socket = io(window.location.origin)
        const disconnectSocket = () => {
            socket.emit('unregister', {
                'session_id': sessionId,
                'username': name
            })
            socket.disconnect()
            socket.close()
        }

        socket.on('connect', () => {
            status.innerText = 'Registering...'
            socket.emit('register', {
                'session_id': sessionId,
                'username': name
            })
        })

        socket.on('register', isRegistered => {
            if (!isRegistered) {
                status.innerText = 'Could not register'
                submit.disabled = false
                disconnectSocket()
            }

            status.innerText = 'Submitting...'
            $.ajax({
                url: `/api/submit/${sessionId}`,
                method: 'POST',
                contentType: false,
                processData: false,
                data: formData,
                success: res => {
                    status.innerText = 'Evaluating...'
                    const json = JSON.parse(res).result
                    if (json.token) {
                        localStorage.setItem(`lognice-token-${sessionId}-${name}`, json.token)
                    }
                },
                error: e => {
                    const message = JSON.parse(e.responseText).message
                    status.innerHTML = `<span style='color: red;'>${message}</span>`
                    submit.disabled = false
                    disconnectSocket()
                }
            })
        })

        socket.on('task_finished', data => {
            if (data.status == 'success') {
                result = data.result
                blocker = result.blocker
                if (blocker) {
                    const ins = blocker.input
                    const inputStr = Object.keys(ins).map(k => `${k}=${ins[k]}`).join(', ')
                    status.innerHTML = `
                        <b style='color: red;'>Your code didn't pass the following test case:</b></br>
                        Input: ${inputStr}</br>
                        Expected output: ${blocker.expected}</br>
                        Actual output: ${blocker.output}`
                } else {
                    status.innerHTML = `
                        <span>You passed all <b style='color: green;'>${result.passed}</b> test cases!</span>
                        <span>CPU Time <b style='color: green;'>${result.time.value} ${result.time.unit}</b></span>`
                }
            } else {
                status.innerHTML = `<span style='color: red;'>${data.message}</span>`
            }
            submit.disabled = false
            disconnectSocket()
        })
    }
}
