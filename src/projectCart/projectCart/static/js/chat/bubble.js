    /**
 * Element
 */
    let chatName = ''
    let chatSocket = null
    let chatWindowUrl = window.location.href
    let chatRoomUuid = ''
    //Elements
    const chatWelcomeElement = document.getElementById("chat_welcome");
    const chatRoomElement = document.getElementById("chat_room");
    const chatBackElement = document.getElementById('back_chat');
    const chatCloseElement = document.getElementById('close_chat');
    
    const buttonBackChat = document.querySelector('#button_back_chat')
    const buttonCloseChat = document.querySelector('#button_close_chat')
    const chatCheckElement = document.querySelector('#check');
    const chatJoinElement = document.querySelector('#chat_join');
    const chatLogElement = document.querySelector('#chat_log');
    const chatNameElement = document.querySelector('#chat_name');
    const chatInputElement = document.querySelector('#chat_message_input');
    const chatSubmitElement = document.querySelector('#chat_message_submit');
    
    /**
     * Function
     *  */ 
    
    function closeButton() {
        chatWelcomeElement.classList.remove("hidden");
        chatRoomElement.classList.add("hidden");
        chatNameElement.value = ''
        chatLogElement.innerHTML = ''
        chatRoomUuid = ''
        chatSocket.close();
    }

    function backButton() {
        chatWelcomeElement.classList.remove("hidden");
        chatRoomElement.classList.add("hidden");
        // chatNameElement.value = ''
        chatSocket.close();
    }

    function scrollToBottom() {
        chatLogElement.scrollTop = chatLogElement.scrollHeight
    }
    
    function getCookie(name) {
        var cookieValue = null
    
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';')
    
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim()
                
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
    
                    break
                }
            }
        }
    
        return cookieValue
    }
    
    function sendMessage() {
        chatSocket.send(JSON.stringify(
            {
                'type': 'message',
                'message': chatInputElement.value,
                'name': chatName
            }
        ))
    
        chatInputElement.value = ''
    }
    
    function onChatMessage(data) {
        console.log('onChatMessage', data)
        // buttonCloseChat.addEventListener('click', closeButton());  
    
        if (data.type == 'chat_message') {
            let tmpInfo = document.querySelector('.tmp-info')
            // buttonCloseChat.addEventListener('click', closeButton);
            
            if(tmpInfo){
                tmpInfo.remove()
            }
    
            if (data.agent) {
                chatLogElement.innerHTML += `
                    <div class="d-flex flex-row justify-content-start mb-4">
                        <div data-initials="${data.initials}"></div>
                        <div>              
                            <p class="small p-2 ms-3 mb-1 mt-3 rounded-3" style="background-color: #ffffff;">${data.message}</p>
                            <p class="small ms-3 mb-1 rounded-3 text-muted">${data.created_at} ago</p>
                        </div>
                    </div>
                `
                
            } else {
                chatLogElement.innerHTML += `
                    <div class="d-flex flex-row justify-content-end mb-4">
                        <div>
                            <p class="small p-2 me-3 mb-1 mt-3 text-white rounded-3" style="background-color: #349afa;">${data.message}</p>
                            <p class="small me-3 rounded-3 text-muted d-flex justify-content-end">${data.created_at} ago</p>
                        </div>
                        <div data-initials="${data.initials}"></div>
                    </div>
                ` 
            }
        } else if(data.type == 'users_update'){
            chatLogElement.innerHTML += '<p class="small text-center "> The admin/agent has joined the chat! </p>'
        } else if(data.type == 'writing_active') {
            if (data.agent) {
                let tmpInfo = document.querySelector('.tmp-info')
                
                if(tmpInfo){
                    tmpInfo.remove()
                }

                chatLogElement.innerHTML += `
                        <div class="tmp-info">
                            <div class="d-flex flex-row justify-content-start mb-4">
                                <div data-initials="${data.initials}"></div>
                                <div>
                                    <p class="small p-3 me-3 mt-3 rounded-3 text-muted">The agent/admin is typing...</p>
                                </div>
                            </div>
                        </div>
                    `
            }
        }
    
        scrollToBottom()
    }
    
    async function joinChatRomm(){
        // console.log('joinChatRoom')
        chatName = chatNameElement.value
        let chatRoomUuid = Math.random().toString(36).slice(2, 12)
        
        console.log('join as :', chatName)
        console.log('Room id :', chatRoomUuid)
    
        const data = new FormData()
        data.append('name', chatName)
        data.append('url', chatWindowUrl)
    
        await fetch(`/api/create-room/${chatRoomUuid}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: data
        })
        .then(function(res) {
            return res.json()
        })
        .then(function(data) {
            console.log('data:', data)
        })
    
        chatSocket = new WebSocket(`ws://${window.location.host}/ws/${chatRoomUuid}/`);
    
        chatSocket.onmessage = function(e) {
            console.log('onmessage')
            onChatMessage(JSON.parse(e.data))
            buttonCloseChat.addEventListener('click', closeButton);  
            buttonBackChat.addEventListener('click', backButton);  
        }
    
        chatSocket.onopen = function(e) {
            console.log('onopen - chat socket was opened')
            scrollToBottom()
        }
    
        chatSocket.onclose = function(e) {
            console.log('onClose - chat socket was closed')
        }
    
    }
    

    chatCheckElement.onclick = function(e) {
        chatWelcomeElement.classList.remove("hidden");
        chatBackElement.classList.add("hidden");
        chatCloseElement.classList.add("hidden");
        
    }

    chatInputElement.onclick = function (e) {
        chatSubmitElement.classList.remove('disabled')
    }
    
    chatJoinElement.onclick = function(e) {
        chatWelcomeElement.classList.add("hidden");
        chatBackElement.classList.remove("hidden");
        chatCloseElement.classList.remove("hidden");
        chatRoomElement.classList.remove("hidden");
        console.log('test')
        joinChatRomm();
    }

    chatNameElement.onclick = function(e) {
        chatJoinElement.classList.remove('disabled')
    }
    
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
            'name': chatName
            }))
    }