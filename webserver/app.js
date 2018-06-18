var express = require('express');
var path = require('path');
var app = express();

app.set("view engine", 'ejs');
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', function (req, res) {
  res.render('index');
});

app.get('/sync_measure', function (req, res) {
  res.render('sync_measure');
});

app.get('/detail', function (req, res) {
  res.render('detail');  
});

app.listen(8080, function () {
  console.log('Server On!');
});
