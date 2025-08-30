fetch('/user/workshops?lat=12.34&long=56.78&radius=10', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
}).then(response => response.json()).then(data => {
  // Populate list/card/map with data
});