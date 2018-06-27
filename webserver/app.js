var express = require('express');
var path = require('path');
var bodyParser = require('body-parser');
var request = require('request');
var wav = require('wav');
var app = express();

app.set("view engine", 'ejs');
app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.raw({ type: 'audio/wav', limit: '50mb' }));

const script_list = [
  {
    "id": 0,
    "movieName": "베테랑",
    "actorName": "유아인",
    "sentence": "어이가 없네",
    "image": "example1.jpeg",
    "movie": "example1.mp4",
    "movieSelected": "example1.mp4#t=4,15",
    "recordTime": 5,
    "description" : "세상 무서울 것 없는 재벌 3세 안하무인 조태오(유아인)가 분노를 표출하는 장면",
    "subtitle" : "WEBVTT\n\n1\n00:00:00.100 --> 00:00:02.000\n이런 상황을 어이가 없다고 그래요\n\n2\n00:00:02.000 --> 00:00:06.000\n황당하잖아 아무것도 아닌 손잡이 때문에 해야될 일을 못하니깐\n\n3\n00:00:08.00 --> 00:00:10.000\n지금 내 기분이 그래\n\n4\n00:00:11.500 --> 00:00:20.000\n어이가 없네",
  },
  {
    "id": 1,
    "movieName": "해바라기",
    "actorName": "김래원",
    "sentence": "속이 후련했냐",
    "image": "example2.jpeg",
    "movie": "example2.mp4",
    "movieSelected": "example2.mp4#t=3.5,16",
    "recordTime": 7,
    "description" : "꼭 그렇게 다 가져가야만 속이 후련했냐!!",
    "subtitle" : "WEBVTT\n\n1\n00:00:00.100 --> 00:00:04.500\n니네 꼭 그랬어야되냐\n\n2\n00:00:05.000 --> 00:00:09.500\n니네 그러면 안 됐어\n\n3\n00:00:10.000 --> 00:00:16.000\n꼭 그렇게 다 가져가야만 속이 후련했냐!!",
  }
];

app.get('/', function (req, res) {
  res.render('index');
});

app.get('/sync_measure', function (req, res) {
  res.render('mimic/sync_measure', {script_list: script_list});
});

app.get('/detail/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('mimic/detail', {script: script_list[s_id]});
});

app.get('/preview/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('mimic/preview', {script: script_list[s_id]});
});

app.get('/practice_mimic/:id', function (req, res) {
  var s_id = req.params.id
  res.render('mimic/practice_mimic', {script: script_list[s_id]});
});

app.post('/practice_mimic/:id', function (req, res) {
  var s_id = req.params.id;
  console.log("RECIEVED AUDIO TO EXTRACT INDICATORS: ", req.body);
  var d = new Date();
  var filename = d.toISOString().slice(0,10).replace(/-/g,"") + d.toISOString().slice(11,19).replace(/:/g,"");

  var writer = new wav.FileWriter(path.join('/', 'seongdalAudio', 'recorded', filename + '.wav'), req.body);

  // TODO: save req.body as wav file

  // TODO: execute python server in order to get the score

  // TODO: recieve score from python server
  var options = {};
  if (id == 0) {

    // ain
    var req_url = 'http://localhost:808/score?fn=' + filename + '&origin=ain';

  }else if (id == 1){

    // raewon
    var req_url = 'http://localhost:808/score?fn=' + filename + '&origin=raewon';
  }

  request.get(req_url,options,function(err,res,body){
   if(err) {
     console.log(err);
   }
   if(res.statusCode !== 200 ) {
     console.log("status code not 200!");
   }
   console.log("res: " + JSON.stringify(res));
   console.log("body: "+ body);
  });
  //TODO Do something with response

      // Pitch Code
      // 0: Good, 1: Low, 2:High
      // Length Code
      // 0: perfect, 1:fast, 2:slow
      // Env code
      // 0: good, 1: bad
      // score
      // itself

  // });
  res.redirect('mimic/practice_mimic/'+s_id);
});

app.get('/mimic_score/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('mimic/mimic_score', {script: script_list[s_id]});
});

app.get('/dubbing', function (req, res) {
  res.render('dubbing/dubbing', {script_list: script_list});
});

app.get('/dubbing/detail/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('dubbing/detail', {script: script_list[s_id]});
});

app.get('/dubbing/preview/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('dubbing/preview', {script: script_list[s_id]});
});

app.get('/dubbing/practice_dubbing/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('dubbing/practice_dubbing', {script: script_list[s_id]});
});

app.get('/gallery', function (req, res) {
  res.render('gallery/gallery', {script_list: script_list});
});

app.get('/gallery/detail/:id', function (req, res) {
  var s_id = req.params.id;
  res.render('gallery/detail', {script: script_list[s_id]});
});

app.listen(8080, function () {
  console.log('Server On!');
});
