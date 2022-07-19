import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.6/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.6.6/firebase-analytics.js";

const firebaseConfig = {
  apiKey: "AIzaSyCEMrtlp1Rncetvn11FYZFeqTriXt2b_dw",
  authDomain: "keylogging-ide.firebaseapp.com",
  projectId: "keylogging-ide",
  storageBucket: "keylogging-ide.appspot.com",
  messagingSenderId: "685589642452",
  appId: "1:685589642452:web:4db158cae59b2d13d68f41",
  measurementId: "G-976S45SE8Q",
  databaseURL: "https://keylogging-ide-default-rtdb.firebaseio.com/"
};

firebase.initializeApp(firebaseConfig);

var uid = "";

firebase.auth().onAuthStateChanged((user) => {
  if (user) {
    // User is signed in, see docs for a list of available properties
    // https://firebase.google.com/docs/reference/js/firebase.User
    uid = user.uid;

    document.getElementById("uid").innerHTML = uid;
  }
});

function googleSignin() {
   firebase.auth()

   .signInWithPopup(provider).then(function(result) {
      var token = result.credential.accessToken;
      var user = result.user;

      uid = user.uid;

      document.getElementById("uid").innerHTML = uid;

   }).catch(function(error) {
      var errorCode = error.code;
      var errorMessage = error.message;

      console.log(error.code)
      console.log(error.message)
   });
}

document.getElementById("signin").onclick = function() {
  googleSignin();
}


var realStartTime;
var paused = true;

var goright = false;
var goleft = false;

function start() {

  document.getElementById("slider3").value = 0;

  realStartTime = Date.now();
  var startTime = Date.now();

  var speed = parseInt(document.getElementById("slider2").value);
  var p2 = parseInt(Math.pow(2, (speed - 500) / 100) * 100) / 100;

  document.getElementById("status").innerHTML = "going";

  speed = p2;


  var id = document.getElementById("subbox").value;
  var prob = parseInt(document.getElementById("subbox2").value)-1;

  var dbRef = firebase.database().ref(id + "/keystrokes");

  var edits = [];
  var lang = "python";
  dbRef.on("value", function(snapshot) {
    if (snapshot != null && snapshot.val() != null) {
      var vl = snapshot.val();
      console.log(vl);
      var ks = Object.getOwnPropertyNames(vl);
      console.log(ks.length);
      for (var i = 0 ; i < ks.length ; i++) {

      }
      ks = Object.getOwnPropertyNames(vl[prob]);
      for (var i = 0 ; i < ks.length ; i++) {
        var val = vl[prob][ks[i]];
        if (ks[i] == "language") {
          lang = snapshot.val()[ks[i]];
        }
        else {

          edits.push([parseInt(ks[i]), val["row"], val["col"], val["oldcode"], val["newcode"], val["index"]]);
        }
      }
      edits[0][3] = "";
      console.log(edits);
    }
  });

  var signature = parseInt(Math.random()*100);
  var last = -1;
  var cur = -1;
  var upto = -1;
  var diff = -1;
  var ind = 0;
  var pos = 0;
  var lupto = -1;

  var loaded = false;

  var code = "";

  var start = -1;
  var end = -1;

  function applyEdit(edit, ei) {

    code = code.split("");

    var line = 1;
    var col = 0;

    var ind = code.length;

    var newcode = "";


    ind = edit[5];

    for (var i = 0 ; i < ind ; i++) {
      newcode += code[i];
    }


    newcode += edit[4];

    for (var i = ind + edit[3].length ; i < code.length ; i++) {
      newcode += code[i];
    }

    code = newcode;

    document.getElementById("txt").value = code.split("\n").join("~~~");

  }

  function applyReverseEdit(edit, ei) {

    code = code.split("");

    var line = 1;
    var col = 0;

    var ind = code.length;

    var newcode = "";


    ind = edit[5];

    for (var i = 0 ; i < ind ; i++) {
      newcode += code[i];
    }

    newcode += edit[3];

    for (var i = ind + edit[4].length ; i < code.length ; i++) {
      newcode += code[i];
    }

    code = newcode;

    document.getElementById("txt").value = code.split("\n").join("~~~");

  }

  function animate() {

    var spd = parseInt(document.getElementById("slider2").value);
    var p2 = parseInt(Math.pow(2, (spd - 500) / 100) * 100) / 100;


    speed = p2;

    if (startTime != realStartTime) return;

    if (!loaded && edits.length > 0) {

      var editor = ace.edit("editor");
      editor.setTheme("ace/theme/textmate");
      editor.session.setMode("ace/mode/" + lang);

      loaded = true;
      upto = edits[0][0];
      start = edits[0][0];
      end = edits[edits.length - 1][0] + 1;
      last = Date.now();

    }

    if (loaded && last != -1) {

      cur = Date.now();

      if (!paused) {
        document.getElementById("slider3").value = parseFloat(document.getElementById("slider3").value) + ((cur - last) / (end - start)) * 1000 * speed;
      }

      pos = parseFloat(document.getElementById("slider3").value);

      diff = (cur - last) * speed;

      upto = (pos / 1000) * (end - start) + start;


      if (ind >= edits.length) {
        document.getElementById("status").innerHTML = "done";
      }

      if (goright && ind < edits.length) {
        console.log("right" + " " + ind + " " + edits.length);
        applyEdit(edits[ind], ind);
        upto = edits[ind][0];
        ind++;
        document.getElementById("slider3").value = ((upto - start) / (end - start)) * 1000;
      }
      else if (goleft && ind > 1) {
        console.log("left" + " " + ind + " " + edits.length);
        applyReverseEdit(edits[ind-1], ind-1);
        upto = edits[ind-2][0];
        ind--;
        document.getElementById("slider3").value = ((upto - start) / (end - start)) * 1000;
      }
      else if (upto > lupto) {
        while (ind < edits.length && edits[ind][0] < upto) {
          //if (ind < 82) {
            applyEdit(edits[ind], ind);
          //}
          ind++;
        }
      }
      else if (upto < lupto) {
        while (ind-1 >= 0 && edits[ind-1][0] > upto) {
          //if (ind < 82) {
            applyReverseEdit(edits[ind-1], ind-1);
          //}
          ind--;
        }
      }


      last = cur;
      lupto = upto;

      goright = false;
      goleft = false;


    }
    window.requestAnimationFrame(animate, 1);
  }



  animate();
}

function play() {
  paused = false;
  document.getElementById("play").hidden = true;
  document.getElementById("pause").hidden = false;
  document.getElementById("left").hidden = true;
  document.getElementById("right").hidden = true;
}

function pause() {
  paused = true;
  document.getElementById("play").hidden = false;
  document.getElementById("pause").hidden = true;
  document.getElementById("left").hidden = false;
  document.getElementById("right").hidden = false;
}

function left() {
  goleft = true;
}

function right() {
  goright = true;
}

//if (uid.length > 0) {
  document.getElementById("go").addEventListener('click', event =>  {
    start();
  });

  document.getElementById("play").addEventListener('click', event =>  {
    play();
  });

  document.getElementById("pause").addEventListener('click', event =>  {
    pause();
  });

  document.getElementById("right").addEventListener('click', event =>  {
    right();
  });

  document.getElementById("left").addEventListener('click', event =>  {
    left();
  });
//}
