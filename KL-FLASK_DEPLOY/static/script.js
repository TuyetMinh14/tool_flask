
// update text sau khi select
function get_text(id_para, id_qs, question = null) {
  var select = document.getElementById("selectable-text-area");

  if (window.getSelection) {
    var text = window.getSelection().toString().trim();
    var selection = window.getSelection();
    // var range = selection.getRangeAt(0); // Get the range of the selection
    // var startOffset = range.startOffset; // Starting offset of the selection
    // startOffset = startOffset - 10;

    // Calculate the number of words in the selection
    var words = text.length;

    if (words > 384) {
      console.log("Selection exceeds 384 words limit.");
      var myButton = document.getElementById("selectButton");
      myButton.disable = true;
      alert("Limited word");
      return;
    }

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
            

          // start_offset: startOffset, // Include start offset in the request
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          window.location.href = data.redirect_url;
          // Xử lý phản hồi từ máy chủ nếu cần
        })
        .catch((error) => {
          console.error("There was a problem with the fetch operation:", error);
        });
    } else {
      console.log("Không có văn bản nào được chọn.");
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
    displayF1 < 0.5 &&
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
  var qa_id_text = document.getElementById("qa_id").innerText;

  // Lấy các phần tử cần thiết
  var saveButton = document.getElementById("saveButton");

  // Gán sự kiện click cho nút "Save"
  saveButton.addEventListener("click", function () {
    saveChanges(qa_id_text);
  });

  // Gán sự kiện keypress cho input
  document.addEventListener("keypress", function (event) {
    // Kiểm tra nếu phím được nhấn là phím "Enter" và .confirmation-form đang hiển thị
    if (event.key === "Enter" && confirmationFormIsVisible()) {
      saveChanges(qa_id_text);
    }
  });

  var confirmationForm = document.querySelector(".confirmation-form");

  var closeButton = document.getElementById("closeButton");

  closeButton.addEventListener("click", function () {
    if (confirmationFormIsVisible()) {
      confirmationForm.style.display = "none";
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && confirmationFormIsVisible()) {
      confirmationForm.style.display = "none";
    }
  });
});
function confirmationFormIsVisible() {
  var confirmationForm = document.querySelector(".confirmation-form");
  return confirmationForm && confirmationForm.style.display === "block";
}

function saveChanges(qa_id) {
    var questionInput = document.querySelector("#question");
    var question = questionInput.value.trim();
    var answer = document.getElementById("displaySelectedquestion").innerText;

    var content = document.getElementById("selectable-text-area").innerText;
    var startOffset = content.indexOf(answer);
    var type_ans = document.getElementById('Type_answer').value;
    var type_question = document.getElementById('type_question').value;
    var Dificult = document.getElementById('Dificult').value;

    console.log(type_question)
    let fake_id = "AD_01_" + qa_id + "_" + type_question + "_" + Dificult + "_" + type_ans;
    fetch("/save_qa_changes", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            question: question,
            answer: answer,
            qa_id: qa_id,
            startOffset: startOffset,
            fake_id: fake_id,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data.message); // Hiển thị thông báo thành công hoặc xử lý logic khác ở đây
        })
        .catch((error) => {
            console.error("Error:", error);
        });

    // Ẩn form sau khi lưu
    var confirmationForms = document.getElementsByClassName("confirmation-form");
    document.getElementById('Type_answer').style.color = "black";
    document.getElementById('type_question').style.color = "black";
    document.getElementById('Dificult').style.color = "black";
    document.getElementById('question').style.color = "blue";
    document.getElementById('displaySelectedquestion').style.color = "blue";
    

    for (var i = 0; i < confirmationForms.length; i++) {
        var confirmationForm = confirmationForms[i];
        confirmationForm.style.display = "none";
    }
}


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

                // Xử lý dữ liệu của tệp JSON thứ hai
                var fileName2 = responseData.files[1].file_name;
                var data2 = responseData.files[1].data;

                var jsonString2 = JSON.stringify(data2, null, 2);
                var blob2 = new Blob([jsonString2], { type: "application/json" });
                var url2 = URL.createObjectURL(blob2);

                var a2 = document.createElement("a");
                a2.href = url2;
                a2.download = fileName2;

                document.body.appendChild(a2);
                a2.click();
                document.body.removeChild(a2);
            })
            .catch(error => {
                console.error("Lỗi khi xuất tệp JSON:", error);
            });
    });
});















