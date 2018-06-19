var express = require('express');
var path = require('path');
var app = express();

app.set("view engine", 'ejs');
app.use(express.static(path.join(__dirname, 'public')));

const script_list = [
  {
    "id": 0,
    "movieName": "베테랑",
    "actorName": "유아인",
    "sentence": "어이가 없네",
    "image": "example1.jpeg",
    "movie": "example1.mp4",
    "description" : "세상 무서울 것 없는 재벌 3세 안하무인 조태오(유아인)가 분노를 표출하는 장면",
    "subtitle" : "WEBVTT\n\n1\n00:00:02.500 --> 00:00:05.250\nInstead of loading an external .vtt file,\n\n2\n00:00:05.250 --> 00:00:09.750\nThe workaround is to embed it inside a script tag,\n\n3\n00:00:10.001 --> 00:00:15.000\nAnd then parse it using JavaScript\nand dynamically add it as a new TextTrack.",
  },
  {
    "id": 1,
    "movieName": "해바라기",
    "actorName": "김래원",
    "sentence": "속이 후련했냐",
    "image": "example2.jpeg",
    "movie": "example2.mp4",
    "description" : "꼭 그렇게 다 가져가야만 속이 후련했냐!!",
    "subtitle" : "WEBVTT\n\n1\n00:00:00.500 --> 00:00:04.500\n꼭 그렇게 다 가져가야만\n\n2\n00:00:04.750 --> 00:00:09.750\n 속이 후련했냐!!",
  }
];

app.get('/', function (req, res) {
  res.render('index');
});

app.get('/sync_measure', function (req, res) {
  res.render('sync_measure', {script_list: script_list});
});

app.get('/detail/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('detail', {script: script_list[s_id]});
});

app.get('/preview/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('preview', {script: script_list[s_id]});
});

app.listen(8080, function () {
  console.log('Server On!');
});
