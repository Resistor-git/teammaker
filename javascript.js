// automatically reloads content
// https://www.youtube.com/watch?v=x5trGVMKTdY&t=5382s https://developer.mozilla.org/ru/docs/Web/API/Fetch_API/Using_Fetch
// takes response from server and draws <p> with games' names
function lobbies_names() {
    fetch("/lobbies_names")
    .then(response => response.json())
    .then(data => {
        // data is "Object { lobbies_names: ["Overwatch", "Starcraft 2", "Counter-Strike", … ] }"
        // console.log(data)
        //console.log(data.lobbies_names)
        for (el of data.lobbies_names){
            // console.log(el)
            var tag = document.createElement("p");
            tag.setAttribute("id", el);
            var lobby_name = document.createTextNode(el);
            tag.appendChild(lobby_name);
            var lobby_name_element = document.getElementById("lobbies_names");
            lobby_name_element.appendChild(tag);
        }
    })
}

// takes response from server and draws <ul> after <p> from function "lobbies_names"
function lobbies_users(){
    fetch("/lobbies_users")
    .then(response => response.json())
    .then(data => {
        // data is "Object { "Counter-Strike": ["ssss", "xxxx"], "Heroes of the Storm": […], "Hunt: Showdown": […], … }
        // console.log(data)
        // console.log(data.lobbies_users)
        // console.log(data.lobbies_users.Overwatch)

        $.each(data.lobbies_users, function(key, value) {
            // console.log(key)
            // console.log(value)

            // ids are generated based on games' names from json, some games have spacebar in the name
            let id_without_spaces = key.replace(/ /g, '');

            // this part is for replacing the old <ul> with new one; without this code page will have new <ul> after old <ul>
            try {
                let list_of_players = document.getElementById(id_without_spaces + '_ul');
                //console.log(list_of_players)
                list_of_players.remove()
                // console.log(list_of_players.innerHTML)
            }
            catch(e){
                //console.log("error")
            }

            // lobby_name_element is the name of the lobby, <p>Overwatch</p>
            // .insertAdjacentHTML creates <ul> and <li> with usernames after <p>
            // // "TypeError: lobby_name_element is null" is fine, it just means, that the lobby is empty
            let lobby_name_element = document.getElementById(key);
            lobby_name_element.insertAdjacentHTML('afterend', `<ul id=${id_without_spaces + '_ul'}><li>${value}</li></ul>`);  // pay attention to `` it is grave accent, not quotes
        });
    })
}


// order of these functions calls may be important, or may be not
function lobbies_autoupdate(){
    console.log("autoupdate started")
    document.addEventListener("DOMContentLoaded", lobbies_names);
    document.addEventListener("DOMContentLoaded", lobbies_users);
    setInterval(lobbies_users, 5000);
}



// js https://www.youtube.com/watch?v=x5trGVMKTdY&t=5382s https://developer.mozilla.org/ru/docs/Web/API/Fetch_API/Using_Fetch
// function lobby_updater() {
//     fetch("/lobby_updater")
//     .then(response => response.json())
//     .then(data => {
//         //console.log(data)
//         const lobbies_data = data;
//         //console.log(test)

//         // document.getElementById("test").innerHTML = function() {
//         //     for(var key in test){
//         //         console.log(key);
//         //     }

//         // };


//         for(var lobby in lobbies_data) {
//             // console.log(lobby);
//             // console.log(lobbies_data[lobby])
//             // create html element with name of the lobby(game)
//             if (lobby_name){
//                 lobby_name.remove()
//             } else {
//                 var lobby_name = document.createElement("p");
//                 lobby_name.innerText = lobby;
//                 document.getElementById("lobby_name").appendChild(lobby_name);
//                 // create <ul> with users in lobby
//                 lobbies_data[lobby].forEach(element => {
//                     if (list_of_users_in_lobby || user_in_lobby) {
//                         list_of_users_in_lobby.remove()
//                         user_in_lobby.remove()
//                     } else {
//                         var list_of_users_in_lobby = document.createElement("li");
//                         var user_in_lobby = document.createTextNode(lobbies_data[lobby]);
//                         list_of_users_in_lobby.appendChild(user_in_lobby);
//                         document.getElementById("autoupdated_lobby").appendChild(list_of_users_in_lobby)
//                     }
                        
                    
//                 });
//             }
        

//         }

//     });
// };
// document.addEventListener("DOMContentLoaded", lobby_updater);
// //setInterval(lobby_updater, 10000);





// // Actually working generator of Names + lists (static)
// function lobbies_names() {
//     fetch("/lobbies_names")
//     .then(response => response.json())
//     .then(data => {
//         // console.log(data)
//         console.log(data.lobbies_names)
//         for (el of data.lobbies_names){
//             // console.log(el)
//             var tag = document.createElement("p");
//             tag.setAttribute("id", el);
//             var lobby_name = document.createTextNode(el);
//             tag.appendChild(lobby_name);
//             var element = document.getElementById("lobbies_names");
//             element.appendChild(tag);
//             //
//             var foo = document.createElement("ul");
//             var bar = document.createElement("li");
//             var qqq = document.createTextNode("zzz");
//             foo.appendChild(bar);
//             bar.appendChild(qqq)
//             element.appendChild(foo);
//         }

//     })
// }
//     document.addEventListener("DOMContentLoaded", lobbies_names);
//     //setInterval(lobby_updater, 1000);
