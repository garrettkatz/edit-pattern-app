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

var realStartTime;

function start() {
  realStartTime = Date.now();
  var startTime = Date.now();

  var speed = parseInt(document.getElementById("slider2").value);
  var p2 = parseInt(Math.pow(2, (speed - 500) / 100) * 100) / 100;

  document.getElementById("status").innerHTML = "going";

  speed = p2;

  console.log(speed);

  var id = parseInt(document.getElementById("subbox").value);
  var dbRef = firebase.database().ref(id);
  var edits = [];
  var lang = "python";
  dbRef.on("value", function(snapshot) {
    if (snapshot != null && snapshot.val() != null) {
      var vl = snapshot.val();
      console.log(vl);
      var ks = Object.getOwnPropertyNames(vl);
      for (var i = 0 ; i < ks.length ; i++) {
        if (ks[i] == "language") {
          lang = snapshot.val()[ks[i]];
        }
        else {
          var val = snapshot.val()[ks[i]];
          edits.push([parseInt(ks[i]), val["row"], val["col"], val["oldcode"], val["newcode"], val["index"]]);
        }
      }
      console.log(edits);
    }
  });

  var last = -1;
  var cur = -1;
  var upto = -1;
  var diff = -1;
  var ind = 0;

  var loaded = false;

  var code = "";

  function applyEdit(edit, ei) {

    code = code.split("");

    console.log(edit);


    var line = 1;
    var col = 0;

    var ind = code.length;

    var newcode = "";


    ind = edit[5];

    for (var i = 0 ; i < ind ; i++) {
      newcode += code[i];
    }

    console.log(ind);

    newcode += edit[4];

    for (var i = ind + edit[3].length ; i < code.length ; i++) {
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
      console.log(edits);

      var editor = ace.edit("editor");
      editor.setTheme("ace/theme/textmate");
      editor.session.setMode("ace/mode/" + lang);

      loaded = true;
      upto = edits[0][0];
      last = Date.now();
    }

    if (loaded && last != -1) {
      cur = Date.now();
      diff = (cur - last) * speed;

      upto += diff;


      if (ind >= edits.length) {
        document.getElementById("status").innerHTML = "done";
      }

      while (ind < edits.length && edits[ind][0] < upto) {
        //if (ind < 82) {
          applyEdit(edits[ind], ind);
        //}
        ind++;
      }


      last = cur;
    }
    window.requestAnimationFrame(animate, 1);
  }

  animate();
}

document.getElementById("go").addEventListener('click', event =>  {
  start();
});
