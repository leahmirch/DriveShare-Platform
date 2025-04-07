async function getUserIdByUsername(username) {
    try {
        const response = await fetch(`/get_user_id/${username}`);
        if (response.ok) {
            const data = await response.json();
            return data.user_id;
        } else {
            alert("User not found");
            return null;
        }
    } catch (error) {
        console.error("Error fetching user ID:", error);
        return null;
    }
}

async function sendMessage() {
    const username = document.querySelector("input[name='receiver_name']").value;
    const message = document.querySelector("textarea[name='message']").value;

    if (!username || !message) {
        alert("Please enter both the username and message.");
        return false;
    }
    const receiver_id = await getUserIdByUsername(username);
    if (!receiver_id) {
        alert("Invalid username.");
        return false;
    }
    const form = document.getElementById("sendMessageForm");
    form.action = `/send_message/${receiver_id}`;

    form.submit();
    return false;
}

function openSendMessagePopup(){
    document.getElementById("sendMessagePopup").style.display = "block";
}

function closeSendMessagePopup() {
    document.getElementById('sendMessagePopup').style.display = 'none';
}

function markAsRead(messageId, element) {
    fetch(`/mark_read/${messageId}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            element.classList.remove('unread');
        } else {
            console.error("Failed to mark message as read");
        }
    })
    .catch(error => console.error("Error marking message as read:", error));
}
