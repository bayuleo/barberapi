// Create a request variable and assign a new XMLHttpRequest object to it.
var request = new XMLHttpRequest();
request.responseType = 'json';

// Open a new connection, using the GET request on the URL endpoint
// request.open('GET', '0.0.0.0:5000/user', false);
request.open("GET","0.0.0.0:5000/user")

request.onload = function () {
  // Begin accessing JSON data here
  var data = JSON.parse(this.response);

    data.forEach(movie => {
    // Log each movie's title
    console.log(movie.name);
    });
}

// Send request
request.send();