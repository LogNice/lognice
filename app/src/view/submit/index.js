window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search)
    if (!urlParams.has('session_id')) {
        window.location.replace('/notfound');
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
    const submit = document.querySelector('#submit')

    submit.onclick = () => {
        const formData = new FormData()
        formData.append('solution', new File([jar.toString()], 'solution.py'))

        $.ajax({
            url: `/api/submit/${sessionId}`,
            method: 'POST',
            contentType: false,
            processData: false,
            data: formData,
            success: res => {
                console.log(res)
            },
            error: e => {
                const message = JSON.parse(e.responseText).message
                console.log(message)
            }
        })
    }
}
