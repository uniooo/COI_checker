function readXlsx() {
  var currentYear = new Date().getFullYear();
  var checkYearNum = document.getElementById("years").value;
  var coTime = Number(document.getElementById("times").value);
  var coTimeYears = Number(document.getElementById("times-years").value);
  let nameList = {};
  var input = document.getElementById("input");
  var file = input.files[0];
  var output = document.getElementById("result");

  var reader = new FileReader();

  reader.onload = function (event) {
    output.innerHTML = `</br>`;
    var data = new Uint8Array(event.target.result);
    var workbook = XLSX.read(data, { type: "array" });
    var sheet = workbook.Sheets[workbook.SheetNames[0]];
    var range = XLSX.utils.decode_range(sheet["!ref"]);
    for (let rowNum = range.s.r; rowNum <= range.e.r; rowNum++) {
      var cell = sheet[XLSX.utils.encode_cell({ r: rowNum, c: 0 })];
      var firstName = cell ? cell.v : "";
      cell = sheet[XLSX.utils.encode_cell({ r: rowNum, c: 1 })];
      var lastName = cell ? cell.v : "";
      if (firstName == "") {
        continue;
      }
      nameList[`${firstName} ${lastName}`] = true;
    }

    xmlCoAuthors = readXML();

    let checkAuthors = Object.keys(xmlCoAuthors);
    let resultFound = false; // 用于检查是否有结果
    for (var i = 0; i < checkAuthors.length; i++) {
      let resultYearBox = {};
      let resultTimeBox = {};
      let thisAuthor = checkAuthors[i];
      let coAuthorsAndYears = xmlCoAuthors[thisAuthor];
      let coAuthors = Object.keys(coAuthorsAndYears);
      for (var j = 0; j < coAuthors.length; j++) {
        var coAuthor = coAuthors[j];
        var checkYearList = coAuthorsAndYears[coAuthor];
        if (!nameList[coAuthor]) {
          continue;
        }
        if (Math.max(...checkYearList) >= currentYear - checkYearNum) {
          resultYearBox[coAuthor] = true;
        }
        if (coTime != "" && coTimeYears != "") {
          var count = countNumbers(checkYearList, currentYear - coTimeYears);
          if (count >= coTime) {
            resultTimeBox[coAuthor] = true;
          }
        }
      }
      let str1 = "";
      for (let key in resultYearBox) {
        if (resultYearBox.hasOwnProperty(key)) {
          str1 += `${key}, `;
        }
      }
      if (str1 != "") {
        output.innerHTML += `<div style="padding:20px;"><b><i>${thisAuthor}</i>'s co-authors in ${checkYearNum} year(s):</b> </br> ${str1}</div>`;
        resultFound = true;
      }

      if (coTime != "" && coTimeYears != "") {
        str2 = "";
        for (let key in resultTimeBox) {
          if (resultTimeBox.hasOwnProperty(key)) {
            str2 += `${key}, `;
          }
        }
        if (str2 != "") {
          output.innerHTML += `<div style="padding:20px;"><b><i>${thisAuthor}</i>'s co-authors time(s) >= ${coTime} in ${coTimeYears} year(s):</b> </br> ${str2}</div>`;
          resultFound = true;
        }

        str = "";
        let keys1 = new Set(Object.keys(resultYearBox));
        let keys2 = new Set(Object.keys(resultTimeBox));
        let allAuthors = new Set([...keys1].concat([...keys2]));
        allAuthors.forEach(function (value) {
          str += `${value}, `;
        });
        if (str != "") {
          output.innerHTML += `<div style="padding:20px;"><b><i>${thisAuthor}</i>'s all co-authors required:</b> </br> ${str}</div>`;
          resultFound = true;
        }
      }

      // output.innerHTML += "</br>";
    }

    if (!resultFound) {
      output.innerHTML += `<div style="padding:20px;"><b>No results found for the given criteria.</b></div>`;
    }
  };

  reader.readAsArrayBuffer(file);
}

function readXML() {
  var urls = document.getElementById("urls").value.split("\n");
  if (urls.length === 0) {
    alert("xml url is empty!");
  }
  let xmlCoAuthors = {};

  for (var i = 0; i < urls.length; i++) {
    var tmpInput = urls[i];
    if (tmpInput == "") {
      continue;
    }
    let index = tmpInput.indexOf(":");
    let thisName = tmpInput.substring(0, index);
    let url = tmpInput.substring(index + 1);

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, false);

    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        //You can parse the XML with DOM API here
        var yearOfAuthors = processXML(xhr);
        xmlCoAuthors[thisName] = yearOfAuthors;
      }
    };

    xhr.send(null);
  }
  return xmlCoAuthors;
}

function processXML(xml) {
  var parser = new DOMParser();
  var xmlDoc = parser.parseFromString(xml.responseText, "text/xml");
  let yearOfAuthors = {};

  let rNodes = xmlDoc.getElementsByTagName("r");
  for (let i = 0; i < rNodes.length; i++) {
    var year = Number(rNodes[i].getElementsByTagName("year")[0].textContent);
    var authors = rNodes[i].getElementsByTagName("author");
    for (var j = 0; j < authors.length; j++) {
      var name = authors[j].textContent
        .replace(/[^a-zA-Z\s]|(\s\d)+$/g, "")
        .trim();
      if (!(name in yearOfAuthors)) {
        yearOfAuthors[name] = [year];
      } else {
        yearOfAuthors[name].push(year);
      }
    }
  }
  return yearOfAuthors;
}

function countNumbers(arr, threshold) {
  let count = 0;
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] >= threshold) {
      count++;
    }
  }
  return count;
}
