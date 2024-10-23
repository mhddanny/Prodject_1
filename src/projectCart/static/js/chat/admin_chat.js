/*
        * Element
        */
const chatRoom = document.querySelector('#room_uuid').textContent.replaceAll('"', '')
let chatSocket = null

/**
 * Element
 * */ 
const chatLogElement = document.querySelector('#chat_log')
const chatInputElement = document.querySelector('#chat_message_input')
const chatSubmitElement = document.querySelector('#chat_message_submit')


/**
 * Function
*/

function scrollToBottom() {
    chatLogElement.scrollTop = chatLogElement.scrollHeight
}

function sendMessage() {
    chatSocket.send(JSON.stringify(
        {
            'type': 'message',
            'message': chatInputElement.value,
            'name': document.querySelector("#user_name").textContent.replaceAll('"', ''),
            'agent': document.querySelector("#user_id").textContent.replaceAll('"', '')
        }
    ))

    chatInputElement.value = ''
}

function onChatMessage(data) {
    console.log('onChatMessage', data)

    if (data.type == 'chat_message') {
        let tmpInfo = document.querySelector('.tmp-info')

        if(tmpInfo){
            tmpInfo.remove()
        }

        if (!data.agent) {
            chatLogElement.innerHTML += `
                <div class="d-flex flex-row justify-content-start mb-4">
                    <div data-initials="${data.initials}"></div>
                    <div>
                        <p class="small p-2 ms-3 mb-1 mt-3 rounded-3" style="background-color: #ffffff;">${data.message}</p>
                        <p class="small ms-3 mb-3 rounded-3 text-muted">${data.created_at} ago</p>
                    </div>
                </div>
            `  
        } else {
            chatLogElement.innerHTML += `
                <div class="d-flex flex-row justify-content-end mb-4">
                    <div>
                        <p class="small p-2 me-3 mb-1 mt-3 text-white rounded-3" style="background-color: #349afa;">${data.message}</p>
                        <p class="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">${data.created_at} ago</p>
                    </div>
                    <div data-initials="${data.initials}"></div>
                </div>
            `   
        } 
    } else if(data.type == 'writing_active') {
        if (!data.agent) {
            let tmpInfo = document.querySelector('.tmp-info')

            if(tmpInfo){
                tmpInfo.remove()
            }
            chatLogElement.innerHTML += `
                <div class="tmp-info">
                    <div class="d-flex flex-row justify-content-start mb-4">
                        <div data-initials="${data.initials}"></div>
                        <div>
                            <p class="small p-3 me-3 mt-3 rounded-3 text-muted">The client is typing...</p>
                        </div>
                    </div>
                </div>
            ` 
        }
    }
    scrollToBottom()
}

// WebSocket
chatSocket = new WebSocket(`ws://${window.location.host}/ws/${chatRoom}/`)

chatSocket.onmessage = function(e) {
    console.log('on message')
    onChatMessage(JSON.parse(e.data))
}

chatSocket.onopen = function(e) {
    console.log('on open')
    scrollToBottom()
}

chatSocket.onclose = function(e) {
    console.log('chat socker closed unexpectadly')
} 

/*
 * Evenr Listener
*/

chatInputElement.onkeyup = function(e) {
    if (e.key === 'Enter' ) {
        sendMessage()
    }
}

chatSubmitElement.onclick = function(e) {
    // e.preventDefault()
    
    sendMessage()
}

chatInputElement,onfocus = function (e) {
    chatSocket.send(JSON.stringify({
        'type': 'update',
        'message': 'writing_active',
        'name': document.querySelector("#user_name").textContent.replaceAll('"', ''),
        'agent': document.querySelector("#user_id").textContent.replaceAll('"', '')
        }))
}