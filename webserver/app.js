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
    "subtitle" : "WEBVTT\n\n1\n00:00:00.100 --> 00:00:02.000\n이런 상황을 어의가 없다고 그래요\n\n2\n00:00:02.000 --> 00:00:06.000\n황당하잖아 아무것도 아닌 손잡이 때문에 해야될 일을 못하니깐\n\n3\n00:00:08.00 --> 00:00:10.000\n지금 내 기분이 그래\n\n4\n00:00:11.500 --> 00:00:20.000\n어이가 없네",
  },
  {
    "id": 1,
    "movieName": "해바라기",
    "actorName": "김래원",
    "sentence": "속이 후련했냐",
    "image": "example2.jpeg",
    "movie": "example2.mp4",
    "description" : "꼭 그렇게 다 가져가야만 속이 후련했냐!!",
    "subtitle" : "WEBVTT\n\n1\n00:00:00.100 --> 00:00:04.500\n꼭 그렇게 다 가져가야만\n\n2\n00:00:04.750 --> 00:00:09.750\n 속이 후련했냐!!",
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

app.get('/practice_mimic/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('practice_mimic', {script: script_list[s_id]});
});

app.listen(8080, function () {
  console.log('Server On!');
});
