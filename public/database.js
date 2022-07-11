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

var num = parseInt(Math.random() * 1000000000);

document.getElementById("subtitle").innerHTML = "Session ID: " + num;

firebase.database().ref(num).set({});

var last = -1;
var last2 = -1;
var lastEdit = "";

function updateDatabase() {
  var content = document.getElementById("edit").innerHTML.split("");

  var nc = "";
  var j = 0;
  while (j < content.length) {
    if (j < content.length - 4 && content.slice(j, j+4).join("") == "&lt;") {
      nc += "<";
      j += 4;
    }
    else if (j < content.length - 4 && content.slice(j, j+4).join("") == "&gt;") {
      nc += ">";
      j += 4;
    }
    else if (j < content.length - 5 && content.slice(j, j+5).join("") == "&amp;") {
      nc += "&";
      j += 5;
    }
    else {
      nc += content[j];
      j++;
    }
  }

  content = nc.split("~~~");

  //624255731
  var editor = document.getElementById("editortype").innerHTML;

  var prob = document.getElementById("probid").innerHTML;

  if ((content.length >= 6 && parseInt(content[0]) != last) || (content.length > 6 && parseInt(content[0]) != last2)) {
    console.log(content);
    firebase.database().ref(num + "/" + prob + "/" + content[0]).set({});
    firebase.database().ref(num + "/" + prob + "/" + content[0] + "/oldcode").set(content[1]);
    firebase.database().ref(num + "/" + prob + "/" + content[0] + "/newcode").set(content[2]);
    firebase.database().ref(num + "/" + prob + "/" + content[0] + "/row").set(parseInt(content[3]));
    firebase.database().ref(num + "/" + prob + "/" + content[0] + "/col").set(parseInt(content[4]));
    firebase.database().ref(num + "/" + prob + "/" + content[0] + "/index").set(parseInt(content[5]));
    if (content.length >= 7) {
      firebase.database().ref(num + "/" + prob + "/" + content[0] + "/correct_testcases").set(parseInt(content[6]));
    }
    if (content.length >= 8) {
      firebase.database().ref(num + "/" + prob + "/" + content[0] + "/total_testcases").set(parseInt(content[7]));
    }
  }

  if (editor != lastEdit) {
    console.log("setting");
    firebase.database().ref(num + "/" + prob + "/language").set(editor);
  }

  if (content.length <= 6) {
    last = parseInt(content[0]);
  }
  else {
    last2 = parseInt(content[0]);
  }

  lastEdit = editor;

  var content = document.getElementById("surveyanswers").innerHTML.split("~~~");

  if (content.length > 0) {
    document.getElementById("surveyanswers").innerHTML = "";
    for (var i = 1 ; i < content.length ; i++) {
      firebase.database().ref(num + "/surveys/" + content[0] + "/" + (i-1)).set(content[i]);
    }
  }

  window.requestAnimationFrame(updateDatabase, 1);
}

updateDatabase();
