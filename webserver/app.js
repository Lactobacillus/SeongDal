var express = require('express');
var path = require('path');
var bodyParser = require('body-parser');
var request = require('request');
var wav = require('wav');
var fs = require('fs');
var fs_extra = require('fs-extra');
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
    "movieSelected": "example1.mp4#t=5,15",
    "recordTime": 4,
    "description" : "두려울 것 없는 재벌 3세 안하무인 조태오(유아인)가 분노하는 장면",
    "subtitle" : "WEBVTT\n\n1\n00:00:00.100 --> 00:00:02.000\n이런 상황을 어이가 없다고 그래요\n\n2\n00:00:02.000 --> 00:00:06.000\n황당하잖아 아무것도 아닌 손잡이 때문에 해야될 일을 못하니깐\n\n3\n00:00:08.00 --> 00:00:10.000\n지금 내 기분이 그래\n\n4\n00:00:11.500 --> 00:00:20.000\n어이가 없네",
    "postDelayTime": 10000,
  },
  {
    "id": 1,
    "movieName": "해바라기",
    "actorName": "김래원",
    "sentence": "속이 후련했냐",
    "image": "example2.jpeg",
    "movie": "example2.mp4",
    "movieSelected": "example2.mp4#t=4.5",
    "recordTime": 8,
    "description" : "꼭 그렇게 다 가져가야만 속이 후련했냐!!",
    "subtitle" : "WEBVTT\n\n1\n00:00:00.100 --> 00:00:04.500\n니네 꼭 그랬어야되냐\n\n2\n00:00:05.000 --> 00:00:09.000\n니네 그러면 안 됐어\n\n3\n00:00:09.000 --> 00:00:18.000\n꼭 그렇게 다 가져가야만 속이 후련했냐!!",
    "postDelayTime": 12000,
  },
  {
    "id": 2,
    "movieName": "태조왕건",
    "actorName": "김영철",
    "sentence": "누가 기침소리를 내었는가말이야",
    "image": "example4.jpg",
    "movie": "example4.mp4",
    "movieSelected": "example4.mp4#t=3.5,16",
    "recordTime": 7,
    "description" : "마구니가 가득 찬 신하를 찾기 위해 궁예(김영철)가 호통치는 장면",
    "subtitle" : "WEBVTT\n\n1\n00:00:01.100 --> 00:00:03.700\n누구인가\n\n2\n00:00:03.750 --> 00:00:08.000\n지금 누가 기침 소리를 내었어\n\n3\n00:00:12.500 --> 00:00:15.000\n누가 기침소리를 내었는가 말이야!!",
    "postDelayTime": 10000,
  },
  {
    "id": 3,
    "movieName": "명탐정 코난",
    "actorName": "코난",
    "sentence": "내 이름은 코난, 탐정이죠",
    "image": "example5.jpg",
    "movie": "example5.mp4",
    "movieSelected": "example5.mp4#t=3.5,16",
    "recordTime": 7,
    "description" : "코난이 자기소개를 하면서 초강력 발차기로 범인을 제압하는 장면",
    "subtitle" : "WEBVTT\n\n1\n00:00:00.100 --> 00:00:03.700\n내 이름은 코난, 탐정이죠\n\n2\n00:00:04.000 --> 00:00:06.000\n뭐어??!!\n\n3\n00:00:5.000 --> 00:00:7.300\n에~~~~잇!!4\n00:00:7.600 --> 00:00:9.000\n으아악!!",
    "postDelayTime": 10000,
  },
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
  var s_id = req.params.id;
  res.render('mimic/practice_mimic', {script: script_list[s_id]});
});

app.get('/mimic_score/:id', function (req, res) {

  var s_id = req.params.id;
  var contact = {};
  contact.length = 1;
  contact.pitch = 0;
  contact.envelope = 0;
  contact.score = 84;
  res.render('mimic/mimic_score', {script: script_list[s_id], contact: contact, filename: 'default'});
});

app.get('/mimic_score/:id/:filename', function (req, res){

  var s_id = req.params.id;
  var filename = req.params.filename;

  console.log(s_id);
  console.log(filename);

  if (s_id == 0){

    // ain
    var req_url = 'http://localhost:808/score?fn=' + filename + '&origin=ain';

  }
  else if (s_id == 1){

    // raewon
    var req_url = 'http://localhost:808/score?fn=' + filename + '&origin=raewon';
  }

  var options = {};
  console.log("req_url is " + req_url);
  request.get(req_url,options,function(err,result,body){
    console.log("let's get it!");
     if(err) {
       console.log("request get error!");
       console.log(err);
       return res.json({success: false, message: err});
     } else if(res.statusCode !== 200 ) {
       console.log(res.statusCode);
       console.log("status code not 200!");
       return res.json({success: false, message: err});
     } else {
       console.log("res: " + JSON.stringify(result));
       console.log("body: "+ body);
       var contact = JSON.parse(body)

       console.log(contact.pitch);
       console.log(contact.length);
       console.log(contact.envelope);
       console.log(contact.score);

       res.render('mimic/mimic_score', {script: script_list[s_id], contact: contact, filename: filename});
     }
  });
});

app.get('/mimic_score_popup/:id', function (req, res) {

  var s_id = req.params.id;
  var contact = {};
  contact.length = 1;
  contact.pitch = 0;
  contact.envelope = 0;
  contact.score = 84;
  res.render('mimic/mimic_score_popup', {script: script_list[s_id], contact: contact, filename: 'default'});
});

app.get('/mimic_score_popup/:id/:filename/:score/:pitch/:length/:envelope', function (req, res) {

  var s_id = req.params.id;
  var filename = req.params.filename;
  var score = req.params.score;
  var pitch = req.params.pitch;
  var length = req.params.length;
  var envelope = req.params.envelope;
  var contact = {};

  contact.pitch = pitch;
  contact.length = length;
  contact.envelope = envelope;
  contact.score = score;
  res.render('mimic/mimic_score_popup', {script: script_list[s_id], contact: contact, filename: filename});
});



app.post('/practice_mimic/:id/:filename', function (req, res) {
  var s_id = req.params.id;
  var filename = req.params.filename;

  console.log("RECIEVED AUDIO TO EXTRACT INDICATORS: ", req.body);

  var writer = new wav.FileWriter(path.join('/', 'seongdalAudio', 'recorded', filename + '.wav'),{samplingRate: '8000'});
//    channels: '숫자 1 또는 2'});
  writer.write(req.body);
  writer.end();

  var contact = {};
  contact.length = 0;
  contact.pitch = 0;
  contact.envelope = 0;
  res.render('mimic/mimic_score', {script: script_list[s_id], contact: contact, filename: filename});

  //  res.send('hello world!');
  // Pitch Code
  // 0: Good, 1: Low, 2:High
  // Length Code
  // 0: perfect, 1:fast, 2:slow
  // Env code
  // 0: good, 1: bad
  // score
  // itself
});

app.get('/save/:id/:filename/:mode/:score/:pitch/:length/:envelope', function (req, res) {
  var s_id = req.params.id;
  var filename = req.params.filename;
  var mode = req.params.mode;
  var score = req.params.score;
  var pitch = req.params.pitch;
  var length = req.params.length;
  var envelope = req.params.envelope;

  var filename_new = "안재우_";
  filename_new += s_id + "_";
  filename_new += score + "_" + pitch + "_" + length + "_" + envelope + "_";
  filename_new += (filename+'_slow.wav');

  fs_extra.copy('C:\\seongdalAudio\\recorded\\' + filename+'_slow.wav', path.join(__dirname,'public/voices/mimic', filename_new), function (err) {
    if (err) {
      console.log(err);
    } else {
      console.log('Copied File!: ' + filename);
    }
    // res.render('mimic/detail', {script: script_list[s_id]});
    if (mode == 0) {
      res.redirect('/gallery');
    } else {
      res.redirect('/mimic_score/'+s_id+'/'+filename);
    }
  });
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

app.post('/dubbing/practice_dubbing/:id/:filename', function (req, res) {
  var s_id = req.params.id;
  var filename = req.params.filename;

  console.log("RECIEVED AUDIO TO EXTRACT INDICATORS: ", req.body);

  var writer = new wav.FileWriter(path.join('/', 'seongdalAudio', 'recorded', filename + '.wav'),{samplingRate: '8000'});
//    channels: '숫자 1 또는 2'});
  writer.write(req.body);
  writer.end();

// TODO LIST
  // res render or redirect(WEBHOOK API not implemented yet)
  res.render('dubbing/result', {script: script_list[s_id], filename: filename});
});

app.get('/dubbing/result/:id/:filename', function (req, res) {
  var s_id = req.params.id;
  var filename = req.params.filename;

  if (s_id == 0){

    // ain
    var req_url = 'http://localhost:808/score?fn=' + filename + '&origin=ain';

  }
  else if (s_id == 1){

    // raewon
    var req_url = 'http://localhost:808/score?fn=' + filename + '&origin=raewon';
  }


  var options = {};
  console.log("req_url is " + req_url);
  request.get(req_url,options,function(err,result,body){
    console.log("let's get it!");
     if(err) {
       console.log("request get error!");
       console.log(err);
       return res.json({success: false, message: err});
     } else if(res.statusCode !== 200 ) {
       console.log(res.statusCode);
       console.log("status code not 200!");
       return res.json({success: false, message: err});
     } else {
       console.log("res: " + JSON.stringify(result));
       console.log("body: "+ body);
       var contact = JSON.parse(body)

      console.log('contact: ' + contact);
      fs_extra.copy('C:\\seongdalAudio\\recorded\\' + filename+'_slow.wav', path.join(__dirname,'public/voices/dubbing', filename+'_slow.wav'), function (err) {
        if (err) {
          console.log(err);
        } else {
          console.log('Copied File!: ' + filename);
        }
        // res.render('mimic/detail', {script: script_list[s_id]});
        res.render('dubbing/result', {script: script_list[s_id], filename: filename});
      });
     }
  });
});

app.get('/dubbing/review/:id/:filename', function (req, res) {
  var s_id = req.params.id;
  var filename = req.params.filename;
  res.render('dubbing/review', {script: script_list[s_id], filename: filename});
});

app.get('/gallery', function (req, res) {
  var record_list = [];
  fs.readdirSync(path.join(__dirname, 'public/voices/mimic')).forEach(file => {
    console.log(file);
    var record_arr = file.split("_");
    var record = {};
    record.username = record_arr[0];
    record.scene = record_arr[1];
    record.score = record_arr[2];
    record.pitch = record_arr[3];
    record.length = record_arr[4];
    record.envelope = record_arr[5];
    record.id = record_arr[6];
    record.filename = file;
    record_list.push(record);
  });
  var sortingField = "score";

  record_list.sort(function(a, b) { // 오름차순
      return b[sortingField] - a[sortingField];
  });

  res.render('gallery/gallery', {script_list: script_list, record_list: record_list});
});

app.get('/gallery_time', function (req, res) {
  var record_list = [];
  fs.readdirSync(path.join(__dirname, 'public/voices/mimic')).forEach(file => {
    console.log(file);
    var record_arr = file.split("_");
    var record = {};
    record.username = record_arr[0];
    record.scene = record_arr[1];
    record.score = record_arr[2];
    record.pitch = record_arr[3];
    record.length = record_arr[4];
    record.envelope = record_arr[5];
    record.id = record_arr[6];
    record.filename = file;
    record_list.push(record);
  });
  var sortingField = "id";

  record_list.sort(function(a, b) { // 오름차순
      return b[sortingField] - a[sortingField];
  });

  res.render('gallery/gallery_time', {script_list: script_list, record_list: record_list});
});

app.get('/gallery/review/:id/:filename', function (req, res) {
  var s_id = req.params.id;
  var filename = req.params.filename;
  res.render('gallery/review', {script: script_list[s_id], filename: filename});
});
app.listen(8080, function () {
  console.log('Server On!');
});
