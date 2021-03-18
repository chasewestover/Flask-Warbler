
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