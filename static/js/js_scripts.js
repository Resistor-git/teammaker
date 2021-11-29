/* pay attention to order of functions and when they are called, it may be important
default order:
    function lobbies_names()
    function lobbies_users()
    function create_buttons()
    function test_buttons()
    window.addEventListener('load', starter);
    setInterval(() => {updater()}, 5000);
    function starter()
    function updater()
*/


// user_info_variable has information about current user: username, id (same as "session['user_id]" and id in database)
// user_info_variable is updated by user_info()
// data received from server - Object { user_id: 5, username: "1111" }
// I know that global variables are bad, especially when they are not constants
var user_info_variable = null;

function user_info() {
    fetch("/user_info")
    .then(response => response.json())
    .then(data => {
        // console.log("INFORMATION ABOUT USER", data);
        user_info_variable = data;
    })
} 


// takes response from server and draws <p> with games' names
function lobbies_names() {
    fetch("/lobbies_names")
    .then(response => response.json())
    .then(data => {
        // data is "Object { lobbies_names: ["Overwatch", "Starcraft 2", "Counter-Strike", … ] }"
        for (el of data.lobbies_names){
            // console.log(el)
            // iterate through the array and create <p>gamename</p> for each element
            
            let lobbies_container = document.getElementById("lobbies_names");

            let lobby_div = document.createElement("div");
            lobby_div.setAttribute("class", "box");
            lobby_div.setAttribute("id", el.replace(/ /g, '') + "_box");
            lobbies_container.appendChild(lobby_div);

            let tag = document.createElement("p");
            tag.setAttribute("id", el.replace(/ /g, ''));
            tag.innerHTML = el;
            lobby_div.appendChild(tag);
            
            // create <li> with default value "Lobby is empty"
            let def_ul = document.createElement("ul");
            def_ul.setAttribute("id", "default_ul_" + el.replace(/ /g, ''));
            def_ul.innerHTML = `${'<li id=default_li_' + el.replace(/ /g, '') + '>' + 'Lobby is empty</li>'}`
            lobby_div.appendChild(def_ul);
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

        $.each(data.lobbies_users, function(key, users) {
            // console.log('data.lobbies_users',data.lobbies_users)
            // console.log('key',key)
            // console.log('users', users)

            // ids are generated based on games' names from json, some games have spacebar in the name
            let id_without_spaces = key.replace(/ /g, '');

            // delete default <ul><li>"Lobby is empty"</ul></li> and create new element with non-default value;
            // really empty lobbies remain with default value, because their names are not in data/response and therefore not in .each cycle
            // this should be done only when the lobby is empty and has default values (<ul id="default_ul_NaturalSelection2">)
            if (document.getElementById("default_ul_" + id_without_spaces) !== null){
                console.log('default <ul> detected and will be deleted', document.getElementById("default_ul_" + id_without_spaces));
                document.getElementById("default_ul_" + id_without_spaces).remove();
                // create new <ul> after <p>
                document.getElementById(id_without_spaces).insertAdjacentHTML('afterend', `<ul id=${id_without_spaces + '_ul'}></ul>`);
                let ul = document.getElementById(id_without_spaces + '_ul');

                for (user of users){
                    ul.insertAdjacentHTML('afterbegin', `<li id=${id_without_spaces + '_li' + '_' + user}>${user}</li>`);
                }
            
            // following part is for replacing the old <ul><li> value with new one;
            } else if (document.getElementById(id_without_spaces + '_ul') !== null){
                console.log("non-default <ul> detected and will be deleted", document.getElementById(id_without_spaces + '_ul').innerHTML);
                document.getElementById(id_without_spaces + '_ul').remove()
                // create new <ul> after <p>
                document.getElementById(id_without_spaces).insertAdjacentHTML('afterend', `<ul id=${id_without_spaces + '_ul'}></ul>`);
                let ul = document.getElementById(id_without_spaces + '_ul');
                
                for (user of users){
                    // console.log('user', user)
                    // console.log('users', users)
                    ul.insertAdjacentHTML('beforeend', `<li id=${id_without_spaces + '_li' + '_' + user}>${user}</li>`);
                }
            }
        });

        // take array of empty lobbies from server and set corresponding <li> to 'Lobby is empty' (ARRAY CONSISTS OF ONLY EMPTY LOBBIES)
        // this code deals with situation when according to db lobby empty is empty, but frontend doesn't know about it
        // without these lines lobby will always be populated by one person who left last (until you update whole page manually)
        for (lobby of data.empty_lobbies){
            // console.log(data.empty_lobbies)
            // console.log(lobby)
            let id_without_spaces = lobby.replace(/ /g, '');
            // find lobby and <li> using name of lobby from list of empty lobbies from db
            if (document.getElementById(id_without_spaces + '_ul') !== null){
                document.getElementById(id_without_spaces + '_ul').innerHTML = `${'<li id=default_li_' + id_without_spaces + '>' + 'Lobby is empty</li>'}`
                document.getElementById(id_without_spaces + '_ul').setAttribute("id", "default_ul_" + id_without_spaces)
            }
        }
    })

    // // if lobby becomes empty (<ul> has no <li>) - create <li>'Lobby is empty'</>
    // // .fetch doesn't deal with that, because there are only populated lobbies in array for fetch
    // let div_lobbies_names = document.getElementById("lobbies_names");
    // div_lobbies_names.getElementsByTagName("ul");
    // console.log('!!!', div_lobbies_names.getElementsByTagName("ul"))


    
}


function create_buttons(){
    fetch("/lobbies_names")
    .then(response => response.json())
    .then(data => {
        // data is "Object { lobbies_names: ["Overwatch", "Starcraft 2", "Counter-Strike", … ] }"
        for (lobby of data.lobbies_names){
            // console.log(lobby)
            let id_without_spaces = lobby.replace(/ /g, '');

            // create buttons for default values
            // leave button is not needed, because lobby is already empty
            if (document.getElementById('default_ul_' + id_without_spaces) !== null){
                let create_button_join_lobby = document.getElementById('default_ul_' + id_without_spaces).insertAdjacentHTML('afterend', `
                    <div class="buttons">
                        <form action="/lobbies" method="POST">
                            <input type="hidden" id="game" name="game" value="${lobby}">  <!-- here value should be written same as in db and in json from server, it should contain spaces -->
                            <button id="join_${id_without_spaces}" type="submit">Join lobby</button>
                        </form>
                    </div>
                `);

            // create buttons for non-default values
            } else if (document.getElementById(id_without_spaces + '_ul') !== null){
                let create_button_join_lobby = document.getElementById(id_without_spaces + '_ul').insertAdjacentHTML('afterend', `
                    <div class="buttons">
                        <form action="/lobbies" method="POST">
                            <input type="hidden" id="game" name="game" value="${lobby}">  <!-- here value should be written same as in db and in json from server, it should contain spaces -->
                            <button "join_${id_without_spaces}" type="submit">Join lobby</button>
                        </form>
                    </div>
                `);
                // console.log('button_join_lobby created')

                // creates button only if user is in the lobby
                // document.getElementById(...).textContent returns a string with all users inside <ul> ('testuser1user2nospacesatall')
                // .search(username of the current user) returns -1 if username was not found in <ul>, or index (0,1,2,...) if was found
                // the way .search() works may lead to situations when button is created when it sould be not, example: username = "1111" and he is not in lobby, but there is another user called "vasya1111" who is in lobby
                if (document.getElementById(id_without_spaces + '_ul').textContent.search(`${user_info_variable['username']}`) != -1){
                    // console.log("!!!!!!", document.getElementById(id_without_spaces + '_ul').textContent.search(`${user_info_variable['username']}`))
                    let create_button_leave_lobby = document.getElementById(id_without_spaces + '_ul').insertAdjacentHTML('afterend', `
                    <div class=buttons>
                        <form action="/leave_lobby" method="POST">
                            <input type="hidden" id="game" name="game" value="${lobby}">  <!-- here value should be written same as in db and in json from server, it should contain spaces -->
                            <button id="leave_${id_without_spaces} type="submit">Leave lobby</button>
                        </form>
                    </div>
                `);
                // console.log('button_leave_lobby created')
                }
            }
        }
    });

    let create_button_leave_all_lobbies = document.getElementById('lobbies_names').insertAdjacentHTML('afterend', `
        <div class=buttons>
            <form action="/leave_all_lobbies" method="POST">
                <button id="leave_all_lobbies_button" type="submit">Leave all lobbies</button>
            </form>
        </div>
    `);
    // console.log('button_leave_all_lobbies created')
}
console.log('STATE', document.readyState)




function test_buttons(){
    let create_button_test_lobbies_names = document.getElementById('lobbies_names').insertAdjacentHTML('beforebegin', `
        <input id="test_lobbies_names" type="button" value="lobbies_names" onclick="lobbies_names();" />
    `);
    let create_button_test_lobbies_users = document.getElementById('lobbies_names').insertAdjacentHTML('beforebegin', `
        <input id="test_lobbies_users" type="button" value="lobbies_users" onclick="lobbies_users();" />
    `);
    let create_button_test_create_buttons = document.getElementById('lobbies_names').insertAdjacentHTML('beforebegin', `
        <input id="test_create_buttons" type="button" value="create_buttons" onclick="create_buttons();" />
    `);
    console.log('test buttons finished')
}


// test_buttons();

window.addEventListener('load', starter);

setInterval(() => {
    updater()    
}, 5000);


// called every time page is reloaded: f5, log in/log out, join/leave lobby
function starter(){
    user_info()
    
    console.log('(starter) document state:', document.readyState);
    lobbies_names();
    console.log('lobbies_names is executed');
    setTimeout(() => {
        // execute 400 ms after lobbies_names()
        // promise https://www.youtube.com/watch?v=1idOY3C1gYU
        lobbies_users();
        console.log('lobbies_users is executed');
        
        setTimeout(() => {
            // execute 100 ms after lobbies_users(); some delay is nesessary, bugs at 0 ms
            create_buttons();
            console.log('create_buttons is executed');
        }, 100);
    }, 400);
    console.log('(starter) document state:', document.readyState);
}


function updater(){
    console.log('(updater) document state:', document.readyState);
    lobbies_users();
    console.log('lobbies_users is executed');
    console.log('(updater) document state:', document.readyState);
}

/*     
Скрипты, которые не блокируют DOMContentLoaded:
cкрипты с атрибутом async не блокируют DOMContentLoaded.
cкрипты, сгенерированные динамически при помощи document.createElement('script') и затем добавленные на страницу, также не блокируют это событие.

Если создать листенер с DOMContentLoaded когда страница уже загузилась, то листенер не сработает ?
*/
