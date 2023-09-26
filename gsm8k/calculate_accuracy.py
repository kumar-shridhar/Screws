# some imports
import json
import re
import random
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_file", type=str, default="") 
    parser.add_argument("--sampling_type", type=str, default="subques") # choose between cot or subques
    parser.add_argument("--type", type=str, default="sample") # choose between sample, resample or selection
    parser.add_argument("--hetero", type=bool, default=False)

    return parser.parse_args()

# calculate accuracy
def calculate_accuracy(gt_list, pred_list):
    correct = 0
    for gt, pred in zip(gt_list, pred_list):
        if gt == pred:
            correct += 1
    return (correct / len(gt_list)*100)

# extract ground truth
def extract_gt(gt_sample):
    all_final_ans = []
    for samp in gt_sample:
        final_gt = float(samp.split("#### ")[-1].replace(" ", "").replace(",","").replace("$",""))
        all_final_ans.append(final_gt)
    return all_final_ans

#extract prediction
def extract_pred(pred_sample):
    all_pred = []
    for sample in pred_sample:
        # val = sample.split("The answer is ")[-1]
        pattern = r'[$]?[-+]?\d+(?:\.\d+)?(?:,\d+)*[$]?'
        matches = re.findall(pattern, sample)
        if  matches != []:
            all_pred.append(float(matches[-1].replace(",", "").replace(" ", "").replace("\n", "").replace("$", "").replace("x", "")))
        else:
            all_pred.append(0.0)
            print ("No answer found!")
            print (sample)
    return all_pred

# extract final answers for predictions
def extract_pred_subques(input_pred):
    # split the sentnece after "The answer is" and extract the number
    cleaned_ans = []
    for sentence in input_pred:
        temp = []
        for output in sentence:
            # val = output[1].split("The answer is")[-1]
            pattern = r'[$]?[-+]?\d+(?:\.\d+)?(?:,\d+)*[$]?'
            matches = re.findall(pattern, output[1])
            if  matches != []:
                temp.append(float(matches[-1].replace(",", "").replace(" ", "").replace("\n", "").replace("$", "").replace("x", "")))
        cleaned_ans.append(temp)
    return cleaned_ans

def get_values(RES_PATH, METHOD):

    with open(RES_PATH, "r") as f:
        data_points = list(f)

    predictions, question, answer = [], [], []
    for line in data_points:
        problem = json.loads(line)
        question.append(problem['question'])
        answer.append(problem['answer'])
        predictions.append(problem[METHOD])

    return predictions, question, answer

def print_acc(ans, predictions, sampling_type, VAL):
    gt = extract_gt(ans)
    if sampling_type == "cot":
        pred = extract_pred(predictions)
    else:
        pred_all = extract_pred_subques(predictions)
        pred = [ans[-1] for ans in pred_all]

    #sanity check
    assert len(gt)==len(pred)
    print (f"{VAL} {sampling_type} Accuracy: {calculate_accuracy(gt,pred)}")

def accuracy_final(RES_PATH, SAMPLING_TYPE, METHOD, HETERO):

    if METHOD == "sample":
        sample = "prediction"
        pred, ques, ans = get_values(RES_PATH, sample)
        print_acc(ans, pred, SAMPLING_TYPE, "Sampling")

    elif METHOD == "resample":
        sample = "prediction"
        pred, ques, ans = get_values(RES_PATH, sample)
        print_acc(ans, pred, SAMPLING_TYPE, "Sampling")
        if METHOD == "resample":
            pred, ques, ans = get_values(RES_PATH, "resample")
            print_acc(ans, pred, SAMPLING_TYPE, "Resampling")
            if HETERO:
                pred, ques, ans = get_values(RES_PATH, "het_resample")
                print_acc(ans, pred, "cot", "Heterogeneous Resampling")

    elif METHOD == "selection":
        sample = "prediction"
        pred, ques, ans = get_values(RES_PATH, sample)
        print_acc(ans, pred, SAMPLING_TYPE, "Sampling")
        resample = "resample"
        pred, ques, ans = get_values(RES_PATH, resample)
        print_acc(ans, pred, SAMPLING_TYPE, "Resampling")
        if HETERO:
            pred, ques, ans = get_values(RES_PATH, "het_resample")
            print_acc(ans, pred, "cot", "Heterogeneous Resampling")
        selection = "selection"
        pred, ques, ans = get_values(RES_PATH, selection)
        print_acc(ans, pred, SAMPLING_TYPE, "Selection")

    else:
        print ("Unkonwn {METHOD}. Please choose from 'sample', 'resample' or 'selection' ")


def main(args):
    
    accuracy_final(args.result_file, args.sampling_type, args.type, args.hetero)


if __name__ == "__main__":
    args = get_args()
    assert args.result_file != "", "Please provide the result file path for GSM8K"
    assert args.sampling_type !="", "Please choose between 'cot' or 'subques'"

    main(args)
