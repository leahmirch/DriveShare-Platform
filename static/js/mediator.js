// <<interface>> Mediator
class Mediator {
    notify(sender, event, data) {
        throw new Error("Should be overidden.");
    }
}

export default Mediator;