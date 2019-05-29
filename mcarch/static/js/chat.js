var msgelem = document.getElementById("messages")
var msgbox = document.getElementById("msgbox")

var Message = {
    view: function(vnode) {
        msg = vnode.attrs.msg
        return m(".message", [
            m("span.user", msg.user),
            m("span.content", msg.content),
        ])
    }
}

var MsgList = {
    list: INIT_MSG_LIST,
    view: function() {
        return m(".messages", this.list.map(function(msg) {
            return m(Message, {msg: msg})
        }))
    },
    pushMsg: function(msg) {
        this.list.push(msg)
        m.redraw()
    }
}

m.mount(msgelem, MsgList)


// Listen for messages

var sock = io.connect('http://' + document.domain + ':' + location.port);

sock.on('joined', function(data) {
    console.log("Joined successfully")
})

sock.on('message', function(data) {
    console.log("Received message: " + JSON.stringify(data))
    MsgList.pushMsg(data.msg)
})

sock.on('err', function(data) {
    console.log("Received error message from server: " + data.msg)
})

// Called by onsubmit on the message box.
function sendMessage() {
    sock.emit('send', {chan: CHANNEL_NAME, msg: msgbox.value})
    msgbox.value = ""
}

console.log("Joining channel")
sock.emit('join', {chan: CHANNEL_NAME})


