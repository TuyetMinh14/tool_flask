function highlightAnswer(answer) {
  var context = document.getElementById("selectable-text-area");
  var text = context.innerHTML;
  var highlightedText = '<span style="background-color: #FFFF00">' + answer + '</span>';
  var newText = text.replace(answer, highlightedText);
  context.innerHTML = newText;
}

// update text sau khi select
function get_text(id_para, id_qs, question = null) {
  var select = document.getElementById("selectable-text-area");

  if (window.getSelection) {
    var text = window.getSelection().toString().trim();
    var text2= window.getSelection();
    let selection = window.getSelection();
    var startOffset;
    if (selection.rangeCount > 0) {
      // Get the Range from the Selection
      let range = selection.getRangeAt(0);

      // Calculate the startOffset relative to the whole text content
      let startContainer = range.startContainer;
      startOffset = range.startOffset;

      // Traverse through previous sibling nodes to accumulate offsets
      while (startContainer.previousSibling) {
        startContainer = startContainer.previousSibling;
        startOffset += startContainer.textContent.length;
      }

      let endOffset = startOffset + text2.length;
      
      console.log("Start Offset: ", startOffset);
      console.log("End Offset: ", endOffset);
    }

    // Check if any text is selected
    if (text !== "") {
      fetch("/send_selected_text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_para: id_para,
          id_qs: id_qs,
          selected_text: text,
          question: question,
          startOffset: startOffset,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          var responseUrl = data.redirect_url;
          window.location.href = responseUrl;
        })
        .catch((error) => {
          console.error("There was a problem with the fetch operation:", error);
        });
    } else {
      console.log("No text selected.");
    }
  }
}

function update_question(id_para, id_qs, question, answer = null) {
  // var content = document.getElementById("selectable-text-area").innerText;
  // var answer = document.getElementById("displaySelectedquestion").innerText;

  // var startOffset = content.indexOf(answer);

  fetch("/predict_answer", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: question.value,
      id_para: id_para,
      id_qs: id_qs,
      answer: answer,
      // startOffset: startOffset,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Chuyển hướng người dùng đến URL mới
      window.location.href = data.redirect_url;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function checkInputLength(input) {
  var maxLength = 81; // Số lượng ký tự tối đa cho input
  var currentValue = input.value;
  var nodetext = document.getElementById("question");
  if (currentValue.length > maxLength) {
    nodetext.style.fontSize = "10px";
  }
  var maxLength2 = 150; //
  if (currentValue.length > maxLength2) {
    nodetext.style.fontSize = "8px";
  }
}

function checkF1() {
  var displayF1 = parseFloat(document.querySelector(".displayF1").innerText); // Lấy giá trị displayF1
  var question = document.getElementById("question").value; // Lấy giá trị của input có id là "question"
  var displaySelectedquestion = document.getElementById(
    "displaySelectedquestion"
    ).innerText; // Lấy giá trị của thẻ có id là "displaySelectedquestion"\
    var type_ans = document.getElementById('Type_answer').value;
    var type_question = document.getElementById('type_question').value;
    var Dificult = document.getElementById('Dificult').value;

  if (
    displayF1 < 0.4 &&
    question.trim() !== "" &&
    displaySelectedquestion.trim() !== "" &&
    question.trim() !== "None"
  ) {
      if (!type_ans || !type_question || !Dificult) {
          // Nếu một trong các trường không có giá trị, đặt nền đỏ cho các trường select
          document.getElementById('Type_answer').style.color = "red";
          document.getElementById('type_question').style.color = "red";
          document.getElementById('Dificult').style.color = "red";
          // Hiển thị thông báo hoặc thực hiện xử lý khác tùy thuộc vào yêu cầu của bạn
          alertS("Please select values for all fields.");
          return;
      }
      else { 
    var confirmationForms =
      document.getElementsByClassName("confirmation-form");
    // Lặp qua từng phần tử trong HTMLCollection
    for (var i = 0; i < confirmationForms.length; i++) {
      var confirmationForm = confirmationForms[i];
      confirmationForm.style.display = "block"; // Hiển thị form
    }}
  } else {
    alert("Cannot save");
  }

    
    if (!type_ans || !type_question || !Dificult) {
        // Nếu một trong các trường không có giá trị, đặt nền đỏ cho các trường select
        document.getElementById('Type_answer').style.backgroundColor = "red";
        document.getElementById('type_question').style.backgroundColor = "red";
        document.getElementById('Dificult').style.backgroundColor = "red";
        // Hiển thị thông báo hoặc thực hiện xử lý khác tùy thuộc vào yêu cầu của bạn
        console.log("Please select values for all fields.");
        return; // Không tiến hành lưu
    }
}
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("saveButton").addEventListener("click", function () {
      var data = [];
      var allSelected = true;

      // Iterate through all the questions
      document.querySelectorAll(".toggle-buttons").forEach(function (toggleContainer) {
          var qa_id = toggleContainer.querySelector("input[name='qa_id']").value;
          var selectedInput = toggleContainer.querySelector("input[type='radio']:checked");
        
        // Check if no radio button is selected
        if (!selectedInput) {
            allSelected = false; // Set flag to false if any radio is not selected
            return; // Skip to the next toggleContainer
        }

        var checkValue = selectedInput.value === 'yes' ? 1 : 0;
          data.push({
              id: qa_id,
              check: checkValue
          });
      });

      // Send the collected data to the server
      fetch("/save_qa_changes", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
      })
      .then((response) => response.json())
      .then((data) => {
        alert("Saved successfully!"); // Handle success or other logic here
      })
      .catch((error) => {
        alert("Error:", error);
      });
  });
  
});

document.addEventListener("DOMContentLoaded", function () {

    document.getElementById("exportButton").addEventListener("click", function () {
        // Gửi yêu cầu tới máy chủ để nhận dữ liệu JSON từ cơ sở dữ liệu
        fetch("/export_json")
            .then(response => response.json())
            .then(responseData => {
                // Xử lý dữ liệu của tệp JSON đầu tiên
                var fileName1 = responseData.files[0].file_name;
                var data1 = responseData.files[0].data;

                var jsonString1 = JSON.stringify(data1, null, 2);
                var blob1 = new Blob([jsonString1], { type: "application/json" });
                var url1 = URL.createObjectURL(blob1);

                var a1 = document.createElement("a");
                a1.href = url1;
                a1.download = fileName1;

                document.body.appendChild(a1);
                a1.click();
                document.body.removeChild(a1);

               
            })
            .catch(error => {
              alert("Please ensure that all data entries are checked before proceeding.");
            });
    });
});















