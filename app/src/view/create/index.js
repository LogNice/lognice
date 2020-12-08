window.onload = () => {
    const highlight = editor => {
        editor.textContent = editor.textContent
        hljs.highlightBlock(editor)
    }
    const options = {
        tab: ' '.repeat(4),
        indentOn: /[({:\[]$/
    }
    const jar = CodeJar(document.querySelector('#editor'), withLineNumbers(highlight), options)
    jar.updateCode(
`# 'Validator' class is mandatory
class Validator:
    # so is the 'tests' method
    def tests(self):
        '''Should return an array of dicts, representing test cases'''
        return [
            {
                'input': {'n': i},
                'output': 2 * i
            }
            for i in range(100)
        ]`
    )

    const create = document.querySelector('#create')
    const status = document.querySelector('#status')

    create.onclick = () => {
        create.disabled = true

        const formData = new FormData()
        formData.append('validator', new File([jar.toString()], 'validator.py'))

        $.ajax({
            url: '/api/create',
            method: 'POST',
            contentType: false,
            processData: false,
            data: formData,
            success: res => {
                const sessionId = JSON.parse(res).result.session_id
                const link = `${window.location.origin}/submit?session-id=${sessionId}`
                status.innerHTML = `<span id='status-success'>Session created!</span>
                    <span id='status-success'>People can join the session using the following id: <b style='color: green;'>${sessionId}</b></span>
                    <span id='status-success'>or use the following link: <a href='${link}'>${link}</a></span>`
                create.disabled = false
            },
            error: e => {
                const message = JSON.parse(e.responseText).message
                status.innerHTML = `<span style='color: red;'>${message}</span>`
                create.disabled = false
            }
        })
    }
}
