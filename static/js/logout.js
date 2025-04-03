import mediator from './uiMediator';

document.getElementById('logoutBtn').addEventListener('click', async () => {
    await fetch('/logout');
    mediator.notify(null, 'logout');
});