// automatically reloads content

// js https://www.youtube.com/watch?v=x5trGVMKTdY&t=5382s https://developer.mozilla.org/ru/docs/Web/API/Fetch_API/Using_Fetch
function lobby_updater() {
    fetch("/lobby_updater")
    .then(response => response.json())
    .then(data => {
        //console.log(data)
        const lobbies_data = data;
        //console.log(test)

        // document.getElementById("test").innerHTML = function() {
        //     for(var key in test){
        //         console.log(key);
        //     }

        // };


        for(var lobby in lobbies_data) {
            // console.log(lobby);
            // console.log(lobbies_data[lobby])
            // create html element with name of the lobby(game)
            if (lobby_name){
                lobby_name.remove()
            } else {
                var lobby_name = document.createElement("p");
                lobby_name.innerText = lobby;
                document.getElementById("lobby_name").appendChild(lobby_name);
                // create <ul> with users in lobby
                lobbies_data[lobby].forEach(element => {
                    if (list_of_users_in_lobby || user_in_lobby) {
                        list_of_users_in_lobby.remove()
                        user_in_lobby.remove()
                    } else {
                        var list_of_users_in_lobby = document.createElement("li");
                        var user_in_lobby = document.createTextNode(lobbies_data[lobby]);
                        list_of_users_in_lobby.appendChild(user_in_lobby);
                        document.getElementById("autoupdated_lobby").appendChild(list_of_users_in_lobby)
                    }
                        
                    
                });
            }
        

        }

    });
};
document.addEventListener("DOMContentLoaded", lobby_updater);
//setInterval(lobby_updater, 10000);





// Actually working generator of Names + lists (static)
function lobbies_names() {
    fetch("/lobbies_names")
    .then(response => response.json())
    .then(data => {
        // console.log(data)
        console.log(data.lobbies_names)
        for (el of data.lobbies_names){
            // console.log(el)
            var tag = document.createElement("p");
            tag.setAttribute("id", el);
            var lobby_name = document.createTextNode(el);
            tag.appendChild(lobby_name);
            var element = document.getElementById("lobbies_names");
            element.appendChild(tag);
            //
            var foo = document.createElement("ul");
            var bar = document.createElement("li");
            var qqq = document.createTextNode("zzz");
            foo.appendChild(bar);
            bar.appendChild(qqq)
            element.appendChild(foo);
        }

    })
}
    document.addEventListener("DOMContentLoaded", lobbies_names);
    //setInterval(lobby_updater, 1000);
