from transformers import BertForQuestionAnswering, BertTokenizer
import collections,  torch
import os
def init():
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    model_name='bert-base-multilingual-cased'
    model_checkpoint = current_directory + '\checkpoint-30000'
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForQuestionAnswering.from_pretrained(model_checkpoint)
    return tokenizer, model

def predict_answer(model, tokenizer,question, context, max_seq_length=384, max_answer_length=30):

    # Tokenize question and context
    inputs = tokenizer.encode_plus(question, context, add_special_tokens=True, max_length=max_seq_length, truncation_strategy='only_second', return_tensors="pt")
    input_ids = inputs["input_ids"]
    token_type_ids = inputs["token_type_ids"]

    # Predict
    with torch.no_grad():
        start_logits, end_logits = model(input_ids, token_type_ids=token_type_ids, return_dict=False)

    # Get the most likely answer
    answer_start = torch.argmax(start_logits)
    answer_end = torch.argmax(end_logits)

    # Convert answer tokens to string
    answer = tokenizer.decode(inputs["input_ids"][0][answer_start:answer_end+1], skip_special_tokens=True)

    return answer

def calculate_f1(prediction, ground_truth):
    prediction_tokens = prediction.split()
    ground_truth_tokens = ground_truth.split()

    # Calculate F1 score
    common = collections.Counter(prediction_tokens) & collections.Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)

    return f1
# # Example usage
# if __name__ == "__main__":
#     question = "người được nhắc tới là ai?"
#     context = "Tôi tên Toàn, sinh năm 2003, quê ở Gia Lai. Hiện tại Toàn đang sống ở thành phố Hcm. Toàn trước đây học ở trường cấp 3 tên Nguyễn Trãi. Anh ấy có sở thích vào những con số nên anh ấy đã học trí tuệ nhân tạo."
#     predicted_answer = predict_answer(question, context)
#     print("Predicted answer:", predicted_answer)
