const wrapper = document.querySelector('.login_wrapper');

const login_links = document.querySelectorAll('.login-link');

const register_links = document.querySelectorAll('.register-link');

const institution_links = document.querySelectorAll('.institution-link');

const home = document.querySelector('.home_description_container');

const loginButton = document.querySelector('.btn-pop');

const closebtn = document.querySelector('.icon-close');


register_links.forEach(
    link => {
        link.addEventListener('click', () => {
            wrapper.classList.remove('msg');
            wrapper.classList.remove('institute');
            wrapper.classList.add('active');
        })
    }
)


login_links.forEach(
    link => {
        link.addEventListener('click', () => {
            wrapper.classList.remove('active');
            wrapper.classList.remove('institute');
            wrapper.classList.remove('msg');
        });
    }
);

institution_links.forEach(
    link => {
        link.addEventListener('click', () => {
            wrapper.classList.remove('active');
            wrapper.classList.remove('msg');
            wrapper.classList.add('institute');
        });
    }
);

loginButton.addEventListener('click', () => {
    home.style.display = 'none';
    wrapper.style.display = 'flex';

    wrapper.classList.add('active-pop');
});

closebtn.addEventListener('click', () => {
    wrapper.style.display = 'none';

    wrapper.classList.remove('active-pop');
});

if (document.querySelector('.message')){
    wrapper.classList.add('active-pop');
}