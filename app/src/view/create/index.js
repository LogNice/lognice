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
    const create = document.querySelector('#create')
    const submitLink = document.querySelector('#submit-link')

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
                submitLink.innerHTML = `<span>Session created!</span><span>Use this link to submit solutions:</span><a href='${link}'>${link}</a>`
                create.disabled = false
            },
            error: e => {
                const message = JSON.parse(e.responseText).message
                submitLink.innerHTML = `<span style='color: red;'>${message}</span>`
                create.disabled = false
            }
        })
    }
}
