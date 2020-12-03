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

        const previousToken = localStorage.getItem('lognice_token')
        if (previousToken) {
            formData.append('token', previousToken)
        }

        $.ajax({
            url: `/api/submit/${sessionId}`,
            method: 'POST',
            contentType: false,
            processData: false,
            data: formData,
            success: res => {
                const json = JSON.parse(res).result
                if (json.token) {
                    localStorage.setItem('lognice_token', json.token)
                }
                status.innerText = 'Submitted!'
                submit.disabled = false
            },
            error: e => {
                const message = JSON.parse(e.responseText).message
                status.innerHTML = `<span style='color: red;'>${message}</span>`
                submit.disabled = false
            }
        })
    }
}
