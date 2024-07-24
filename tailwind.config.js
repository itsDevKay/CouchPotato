/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/views/*.{html,ejs,js}"],
    darkMode: 'false',
    theme: {
        extend: {
            colors: {
                'primary-white': '#faf7f7',
                'pt-red': '#eb324b'
            },
        }
    },
    plugins: [],
}