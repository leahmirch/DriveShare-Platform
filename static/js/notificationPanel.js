import UIComponent from './uiComponent';
import mediator from './uiMediator';

class NotificationPanel extends UIComponent{
    displayMsg(message){
        const msgBox = document.getElementById('notification');
        msgBox.innerText = message;
        msgBox.style.display = 'block';
        setTimeout(() => {msgBox.style.display = 'none'; }, 3000);
    }
}

const notificationPanel = new NotificationPanel();
mediator.registerComponent('NotificationPanel', notificationPanel);