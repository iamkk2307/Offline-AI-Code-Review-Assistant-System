// JavaScript Sample Code containing smells and performance issues

var port = 3000; // Style Smell: Use of var

function runServer() {
  console.log("Server starting on port " + port); // Style Smell: console.log left in production
  
  var active = true;
  
  if (active == 1) { // Bug Smell: Loose equality comparison
    // Performance Smell: Nested loops causing potential O(N^2)
    for (var i = 0; i < 1000; i++) {
      for (var j = 0; j < 1000; j++) {
        var val = i * j;
      }
    }
  }
}

function updateDOM(items) {
  var container = document.getElementById("container");
  
  // Performance Smell: innerHTML concatenation inside a loop
  for (var i = 0; i < items.length; i++) {
    container.innerHTML += "<li>" + items[i] + "</li>"; // Inefficient reflow
  }
}

function handleInput(data) {
  // Security Smell: Unsafe eval usage
  eval(data);
}
