const $NEW_MESSAGE_BUTTON = $('.new-message-btn');
const $MESSAGE_AREA= $('#messages')
const $FORM_AREA = $('.form-area')


$('.list-group').on('click', '.messages-like-bottom', toggleLike);

async function toggleLike(e){
    let $icon = $($(e.currentTarget).children()[0]);
    let msgId = $(e.currentTarget).data('msg-id');
    let resp = await axios(
        {url:`/api/messages/${msgId}/like`,
        method:'post'}
    );
    if(resp.data.result === 'success'){
        $icon.toggleClass('fas far');
    }
}

$NEW_MESSAGE_BUTTON.on('click', showNewMessageForm);

function showNewMessageForm() {
    let form = $(
        `<div class="row justify-content-center" id="message-form">
            <div class="col-md-6">
                <div>
                    <textarea placeholder="What's happening?" class="form-control" rows="3"></textarea>
                </div>
                <button class="btn btn-outline-success btn-block" id="msg-submit">Add my message!</button>
             </div>
        </div>
        `
    );
    $FORM_AREA.prepend(form);
}

$FORM_AREA.on('click', '#msg-submit', createNewMessage);

async function createNewMessage(evt) {
    evt.preventDefault();
    const url = '/api/messages/new';
    const msgText = $('textarea').val();
    if (msgText.length > 0) {
        let resp = await axios.post(url,
            {'text': msgText});
        const {msg, user} = resp.data
        console.log(resp)
        appendMessage(msg,user);
        $('#message-form').remove();
    }
}


function appendMessage(msg, user) {
    let newMessage = $(
        `
            <li class="list-group-item">
                <a href="/messages/${msg.id}" class="message-link">
            <a href="/users/${user.id}">
                <img src="${user.image_url}" alt="" class="timeline-image">
            </a>
            <div class="message-area">
                <a href="/users/${ user.id }">@${user.username}</a>
                <span class="text-muted">${ msg.timestamp}</span>
                <p>${ msg.text }</p>
            </div>
            </li>
        `)
    $MESSAGE_AREA.prepend(newMessage)
}
