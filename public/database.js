import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.6/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.6.6/firebase-analytics.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional


// const firebaseConfig = {
//   apiKey: "AIzaSyCEMrtlp1Rncetvn11FYZFeqTriXt2b_dw",
//   authDomain: "keylogging-ide.firebaseapp.com",
//   projectId: "keylogging-ide",
//   storageBucket: "keylogging-ide.appspot.com",
//   messagingSenderId: "685589642452",
//   appId: "1:685589642452:web:4db158cae59b2d13d68f41",
//   measurementId: "G-976S45SE8Q",
//   databaseURL: "https://keylogging-ide-default-rtdb.firebaseio.com/"
// };

const firebaseConfig = {
  apiKey: "AIzaSyCbTIrCVrExm-l3jj1LotrkzwHGdboLE6U",
  authDomain: "aps-keylogger.firebaseapp.com",
  projectId: "aps-keylogger",
  storageBucket: "aps-keylogger.appspot.com",
  messagingSenderId: "3201410277",
  appId: "1:3201410277:web:a80108839d1445841d200c",
  databaseURL: "https://aps-keylogger-default-rtdb.firebaseio.com/"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

var email = "";
var name = "";
var prevname = "";
var uid;
var data;

var thisProgram = parseInt(Math.random()*1000000000);

const provider = new firebase.auth.GoogleAuthProvider();

var done = false;

function applyEdit(code, index, newc, oldc) {

  code = code.split("");

  var line = 1;
  var col = 0;

  var ind = code.length;

  var newcode = "";


  ind = index;

  for (var i = 0 ; i < ind ; i++) {
    newcode += code[i];
  }


  newcode += newc

  for (var i = ind + oldc.length ; i < code.length ; i++) {
    newcode += code[i];
  }

  code = newcode;


  return code;
}

firebase.auth().onAuthStateChanged((user) => {
  if (user) {
    // User is signed in, see docs for a list of available properties
    // https://firebase.google.com/docs/reference/js/firebase.User
    uid = user.uid;
    email = user.email;
    name = user.displayName;

    document.getElementById("uid").innerHTML = uid;
    document.getElementById("email").innerHTML = email;
    document.getElementById("name").innerHTML = name;

    done = false;
    var dbRef = firebase.database().ref(uid);
    dbRef.on("value", function(snapshot) {
      if (snapshot != null && snapshot.val() != null) {

        var vl = snapshot.val();
        var info = vl["info"];
        if (!done && info != undefined) {
          var problem = info["problem"];
          var jscode;
          if (info["jscode"] == undefined) {
            jscode = "";
          }
          else {
            jscode = info["jscode"].join("^^^");
          }
          var pycode;
          if (info["pycode"] == undefined) {
            pycode = "";
          }
          else {
            pycode = info["pycode"].join("^^^");
          }

          var count = info["solvecount"];
          var status = info["status"];
          var time = info["time"];
          var lang = info["lang"];
          var keys = vl["keystrokes"][problem];

          console.log("about to send " + lang);

          var oldcode = "";
          if (keys != undefined) {
            var ks = Object.getOwnPropertyNames(keys);
            if (ks != undefined) {
              var mx = 0;
              var mxi = "";
              ks.sort();
              var edits = [];
              for (var i = 0 ; i < ks.length ; i++) {
                var edit = keys[ks[i]];
                //console.log("problem: " + problem);
                //console.log(edit);
                oldcode = applyEdit(oldcode, edit["index"], edit["newcode"], edit["oldcode"]);
              }
            }
          }

          //console.log("old code: ");
          //console.log(oldcode);

          document.getElementById("preload").innerHTML = [problem, pycode, jscode, count, time, status, lang, oldcode].join("~~~");
          done = true;

        }
        else if (info == undefined) {
          done = true;
        }

      }
    });
    // ...
  } else {
    // User is signed out
    // ...
  }
});

function googleSignin() {
   firebase.auth()

   .signInWithPopup(provider).then(function(result) {
      var token = result.credential.accessToken;
      var user = result.user;


      email = user.email;
      uid = user.uid;
      name = user.displayName;

      document.getElementById("uid").innerHTML = uid;
      document.getElementById("email").innerHTML = email;
      document.getElementById("name").innerHTML = name;

   }).catch(function(error) {
      var errorCode = error.code;
      var errorMessage = error.message;

   });
}

function googleSignout() {
    email = "";
    document.getElementById("restart").innerHTML = "yes";

   firebase.auth().signOut()

   .then(function() {
      console.log('Signout Succesfull')
   }, function(error) {
      console.log('Signout Failed')
   });
}

document.getElementById("signin").onclick = function() {
  googleSignin();
}

document.getElementById("signout").onclick = function() {
  document.getElementById("prelogin").hidden = false;
  document.getElementById("loggedin").hidden = true;

  googleSignout();
}

document.getElementById("restartbutton").onclick = function() {
  firebase.database().ref(uid).set({});
  document.getElementById("restart").innerHTML = "yes";

}




//firebase.database().ref(uid).set({});

var last = -1;
var last2 = -1;
var lastEdit = "";

var lprob;
var lpycode;
var ljscode;
var lcount;
var ldone;
var lstatus;

function updateDatabase() {
  var prob = document.getElementById("send_problem").innerHTML;
  var pycode = document.getElementById("send_pycode").innerHTML.split("~~~");
  var jscode = document.getElementById("send_jscode").innerHTML.split("~~~");
  var count = document.getElementById("send_solvecount").innerHTML;
  var time = document.getElementById("send_timeleft").innerHTML;
  var status = document.getElementById("send_status").innerHTML;
  var lang = document.getElementById("send_lang").innerHTML;

  if (done && lang.length > 0 && prob.length > 0 && pycode.length && jscode.length && ljscode.length && lpycode.length && uid != undefined && (status != lstatus ||  !ldone || prob != lprob || pycode.join("~~~") != lpycode.join("~~~") || jscode.join("~~~") != ljscode.join("~~~") || count != lcount)) {
    firebase.database().ref(uid + "/info/problem").set(prob);
    for (var i = 0 ; i < 1000 ; i++) {
      if (i < pycode.length) {
        firebase.database().ref(uid + "/info/pycode/" + i).set(pycode[i]);
      }
      else if (i >= pycode.length && lpycode[i] && lpycode[i].length) {
        firebase.database().ref(uid + "/info/pycode/" + i).remove();
      }
    }
    for (var i = 0 ; i < 1000 ; i++) {
      if (i < jscode.length) {
        firebase.database().ref(uid + "/info/jscode/" + i).set(jscode[i]);
      }
      else if (i >= jscode.length && ljscode[i] && ljscode[i].length) {
        firebase.database().ref(uid + "/info/jscode/" + i).remove();
      }
    }
    firebase.database().ref(uid + "/info/solvecount").set(count);
    firebase.database().ref(uid + "/info/status").set(status);
    firebase.database().ref(uid + "/info/id").set(thisProgram);
    firebase.database().ref(uid + "/info/time").set(time);

    firebase.database().ref(uid + "/info/lang").set(lang);


  }

  lprob = prob;
  lpycode = pycode;
  ljscode = jscode;
  lcount = count;
  ldone = done;
  lstatus = status;

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
    firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0]).set({});
    firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0] + "/oldcode").set(content[1]);
    firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0] + "/newcode").set(content[2]);
    firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0] + "/row").set(parseInt(content[3]));
    firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0] + "/col").set(parseInt(content[4]));
    firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0] + "/index").set(parseInt(content[5]));
    if (content.length >= 7) {
      firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0] + "/correct_testcases").set(parseInt(content[6]));
    }
    if (content.length >= 8) {
      firebase.database().ref(uid + "/keystrokes/" + prob + "/" + content[0] + "/total_testcases").set(parseInt(content[7]));
    }
  }

  if (editor != lastEdit) {
    firebase.database().ref(uid + "/language").set(editor);
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
      firebase.database().ref(uid + "/surveys/" + content[0] + "/" + (i-1)).set(content[i]);
    }
  }

  window.requestAnimationFrame(updateDatabase, 1);
}

updateDatabase();
