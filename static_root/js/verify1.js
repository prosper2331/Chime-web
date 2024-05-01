const codes = document.querySelectorAll('.code')

codes[0].focus()

codes.forEach((code, idx) => {
    code.addEventListener('input', (e) => {
        const maxLength = code.getAttribute('maxlength')
        const currentValue = code.value

        if(currentValue.length >= maxLength) {
            if(idx < codes.length - 1) {
                codes[idx + 1].focus()
            }
        }
    })

    code.addEventListener('keydown', (e) => {
        if(e.key === 'Backspace' && code.value.length === 0) {
            if(idx > 0) {
                codes[idx - 1].focus()
            }
        }
    })
})
