// UI Mediator Concrete 

import Mediator from './mediator';

class UIMediatorConcrete extends Mediator{
    constructor(){
        super();
        this.components = {};
    }

    registerComponent(name, component){
        this.components[name] = component;
        component.setMediator(this);
    }

    notify(sender, event, data){
        if ( event === "loginSuccess"){
            this.components['NotificationPanel'].displayMsg("Welcome back!");
            this.components['Dashboard'].update(data);
            window.location.href = '/dashboard';
        } else if (event === "loginFailure") {
            this.components['NotificationPanel'].displayMsg("Login failed! Please check your credentials.");
        } else if (event === "logout"){
            this.components['NotificationPanel'].displayMsg("Logged out successfully.");
            window.location.href = "/login";
        } else if (event === 'registrationSuccess') {
            this.components['NotifcationPanel'].displayMsg("Registration successful! Please log in.");
            window.location.hred = "/login";
        } else if (event === "registrationFailure"){
            this.components["NotificationPanel"].displayMsg("Registration failed! Email already registered.");
        }
    }
}

const mediator = new UIMediatorConcrete();
export default mediator;