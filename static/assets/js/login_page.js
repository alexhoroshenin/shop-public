'use strict'

const login_link = document.getElementById('login-link');
const register_link = document.getElementById('register-link');

const register_form = document.getElementById('register-form');
const login_form = document.getElementById('login-form');


function hide_element(e){
    e.classList.add('hidden');
}

function show_element(e){
    e.classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', () =>{

    login_link.addEventListener('click', event => {
        event.preventDefault();
        hide_element(register_form);
        show_element(login_form);
    });

    register_link.addEventListener('click', event => {
        event.preventDefault();
        hide_element(login_form);
        show_element(register_form);
    });

});
