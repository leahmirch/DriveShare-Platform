// <interface>> UIComponent

class UIComponent{
    setMediator(mediator){
        this.mediator = mediator;
    }

    triggerEvent(event, data){
        if (this.mediator){
            this.mediator.notify(this, event, data);
        }
    }
}

export default UIComponent;