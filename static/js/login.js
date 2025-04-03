import UIComponent from './uiComponent';
import mediator from './uiMediator';

class Login extends UIComponent {
    constructor() {
        super();
        this.loginButton = document.getElementById("LoginBtn");
        this.loginButton.addEventListener('click', () => this.handleLogin());
    }

    handleLogin() {
        mediator.notify(this, 'loginAttempt', 'Logging in');
    }
}

const login = new Login();
mediator.registerComponent('login', login);
