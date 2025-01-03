import os
import json
import libem
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
from libem.core.eval import accuracy
from libem.cascade.util import profile
from libem.cascade.function import online
from libem.cascade.match.function import run as match


def benchmark(result):
    cascade_stats = generate_stats(result)
    
    save_results(result, cascade_stats)
    
    plot_result(result, cascade_stats)

    return cascade_stats, result["cascade_result"]


def generate_stats(result):

    args = result["args"]
    train_set = result["train_set"]
    test_set = result["test_set"]
    prematch_model = result["prematch_model"]
    match_model = result["match_model"]
    num_pairs = result["num_pairs"]
    prematch_stats = result["prematch_stats"]
    prematch_results = result["prematch_results"]
    match_stats = result["match_stats"]
    cascade_stats = result["cascade_stats"]
    cascade_result = result["cascade_result"]
    start_time = result["start_time"]
    end_time = result["end_time"]

    print("Prematch Stats: ", prematch_stats)
    print("Match Stats: ", match_stats)

    overall_stat = profile(args, cascade_result, num_pairs)
    overall_stat['throughput'] = libem.round(len(test_set) / (end_time - start_time), 2)
    overall_stat['tokens'] = {}

    prematch_cost = prematch_stats.get('tokens', {}).get('cost', 0)
    match_cost = match_stats.get('tokens', {}).get('cost', 0)
    print(prematch_cost, match_cost)

    overall_stat['tokens']['cost'] = prematch_cost + match_cost
    cascade_stats = {
        "dataset": args.name,
        "stats": overall_stat, 
        "stats by stages": {
            f"Prematch {prematch_model}": prematch_stats,
            f"Match {match_model}": match_stats,
        },
        "results": cascade_result
        }
    
    result["cascade_stats"] = cascade_stats

    # Result when only Prematch model is used
    prematch_single_stats, prematch_single_results = prematch_stats, prematch_results
    
    prematch_single = {
        "dataset": args.name,
        "model": prematch_model,
        "stats": prematch_single_stats,
        "results": prematch_single_results
    }

    # Result when only Match model is used
    match_single_state, match_single_result = match(train_set, test_set, args, model_choice=match_model)

    match_single = {
        "dataset": args.name,
        "model": match_model,
        "stats": match_single_state,
        "results": match_single_result
    }

    return cascade_stats, prematch_single, match_single


def save_results(cascade, prematch_single, match_single):
    # Save the output
    dataset = cascade["dataset"]
    output_path = os.path.join("examples", "cascade", "output", dataset)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Output of the Cascade
    dataset = cascade["dataset"]
    cascade_file_name = f"cascade-{dataset}-{timestamp}.json"
    cascade_file_path = os.path.join(output_path, cascade_file_name)
    os.makedirs(os.path.dirname(cascade_file_path), exist_ok=True)
    with open(cascade_file_path, "w") as json_file:
        json.dump(cascade, json_file, indent=4)

    # Output of the Prematch
    dataset = prematch_single["dataset"]
    prematch_model = prematch_single["model"]
    prematch_file_name = f"{prematch_model}-{dataset}-{timestamp}.json"
    prematch_file_path = os.path.join(output_path, prematch_file_name)
    os.makedirs(os.path.dirname(prematch_file_path), exist_ok=True)
    with open(prematch_file_path, "w") as json_file:
        json.dump(prematch_single, json_file, indent=4)

    # Output of the Match   
    dataset = match_single["dataset"]
    match_model = match_single["model"]
    match_file_name = f"{match_model}-{dataset}-{timestamp}.json"
    match_file_path = os.path.join(output_path, match_file_name)
    os.makedirs(os.path.dirname(match_file_path), exist_ok=True)
    with open(match_file_path, "w") as json_file:
        json.dump(match_single, json_file, indent=4)


def plot_result(cascade, prematch_single, match_single):
    dataset = cascade["dataset"]
    output_path = os.path.join("examples", "cascade", "output", dataset)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    prematch_model = prematch_single["model"]
    match_model = match_single["model"]
    result_prematch = prematch_single["results"]
    result_match = match_single["results"]
    approaches = [prematch_model, match_model, "Cascade"]

    # Plot for F1 Graph
    f1 = [data['stats']['f1'] for data in [prematch_single, match_single, cascade]]
    min_f1, max_f1 = min(f1), max(f1)
    y_margin = 2
    plt.bar(approaches, f1, color='skyblue', label='F1 Score')
    for i, value in enumerate(f1):
        plt.text(i, value + 0.01, f'{value:.2f}', ha='center', va='bottom')
    plt.ylim(min_f1 - y_margin, max_f1 + y_margin)
    plt.ylabel('F1 Score')
    plt.xlabel('Models')
    plt.title('F1 Score', pad=20)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.legend()
    plt.tight_layout()
    file_name = f"f1-comparison-{dataset}-{timestamp}.png"
    plt.savefig(os.path.join(output_path, file_name))
    plt.show()

    # Plot for Cost
    cost = [data['stats']['tokens']['cost'] for data in [prematch_single, match_single, cascade]]
    plt.bar(approaches, cost, color='green', label='Cost')
    for i, value in enumerate(cost):
        plt.text(i, value + 0.0001, f'{value:.5f}', ha='center', va='bottom')
    plt.ylabel('Cost')
    plt.xlabel('Models')
    plt.title('Cost')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.legend()
    plt.tight_layout()
    file_name = f"cost-comparison-{dataset}-{timestamp}.png"
    plt.savefig(os.path.join(output_path, file_name))
    plt.show()

    # Confidence Calibration
    prematch_acc = accuracy_groupby_confidence(result_prematch)
    match_acc = accuracy_groupby_confidence(result_match)
    output_path = os.path.join("examples", "cascade", "output", dataset)
    confidence_calibration_graph(prematch_acc, match_acc, dataset, output_path)


def accuracy_groupby_confidence(data):
    confidence_dict = defaultdict(list)
    for item in data:
        confidence = item['confidence']
        confidence_dict[confidence].append(item)
    
    accuracy_dict = {}

    for confidence, items in confidence_dict.items():
        truth = [item['label'] == 1 for item in items]
        predictions = [item['pred'] == "yes" for item in items]
        acc = accuracy(truth, predictions)
        if len(items) > 5:
            accuracy_dict[confidence] = acc

    keys = accuracy_dict.keys()
    keys = [key for key in keys if key is not None]
    keys_sorted = sorted(keys)
    sorted_dict = {key: accuracy_dict[key] for key in keys_sorted}

    return sorted_dict


def confidence_calibration_graph(prematch_acc, match_acc, dataset, output_path):
    x_gpt4o_mini = list(prematch_acc.keys())
    y_gpt4o_mini = list(prematch_acc.values())
    
    x_gpt4o = list(match_acc.keys())
    y_gpt4o = list(match_acc.values())
    
    perfect_calibration = np.linspace(0, 1, 100)
    
    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(x_gpt4o_mini, y_gpt4o_mini, '-o', label="GPT-4o-mini", color='darkblue', linewidth=1.5, alpha=0.8)
    plt.plot(x_gpt4o, y_gpt4o, '-o', label="GPT-4o", color='red', linewidth=1.5, alpha=0.8)
    plt.plot(perfect_calibration, perfect_calibration, '--', label="Perfect Calibration", color='black', alpha=0.5)
    
    plt.xlabel("Confidence", fontsize=11)
    plt.ylabel("Accuracy", fontsize=11)
    plt.title("Accuracy vs. Confidence", fontsize=12)
    plt.legend(loc='lower right', fontsize=10, frameon=False)
    
    plt.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.6)
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['left'].set_color('white')
    plt.gca().spines['bottom'].set_color('white')
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_name = f"confidence-calibration-{dataset}-{timestamp}.png"
    plt.savefig(os.path.join(output_path, file_name))
    plt.show()


def compare_results(result_data):
    prematch_stats = result_data["prematch_stats"]
    prematch_results = result_data["prematch_results"]
    match_stats = result_data["match_stats"]
    match_results = result_data["match_results"]
    final = result_data["cascade_result"]
    dataset = result_data["dataset"]

    result = []

    for prematch_result in prematch_results:
        for final_result in final:
            if final_result['left'] == prematch_result['left'] and final_result['right'] == prematch_result['right']:
                final_pred = final_result['pred']
                break

        entry = {
            "left": prematch_result['left'],
            "right": prematch_result['right'],
            "label": prematch_result['label'],
            "final_pred": final_pred,
            "prematch_results": {
                "pred": prematch_result['pred'],
                "confidence": prematch_result['confidence'],
                "calibrated_confidence": prematch_result['calibrated_confidence'],
                "explanation": prematch_result['explanation'],
                "model_output": prematch_result['model_output'],
                "tool_outputs": prematch_result['tool_outputs'],
                "latency": prematch_result['latency'],
                "tokens": prematch_result['tokens']
            },
            "match_results": {} 
        }

        for match_result in match_results:
            if match_result['left'] == prematch_result['left'] and match_result['right'] == prematch_result['right']:
                entry['match_results'] = {
                    "pred": match_result['pred'],
                    "confidence": match_result['confidence'],
                    "explanation": match_result['explanation'],
                    "model_output": match_result['model_output'],
                    "tool_outputs": match_result['tool_outputs'],
                    "latency": match_result['latency'],
                    "tokens": match_result['tokens']
                }
                break

        result.append(entry)

    # Output to a JSON file
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_filename = f"results-by-stages-{dataset}-{timestamp}.json"
    output_path = os.path.join("examples", "cascade", "output", dataset)
    output_filepath = os.path.join(output_path, output_filename)
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, "w") as json_file:
        json.dump(result, json_file, indent=4)

    total_pairs = len(result)
    num_prematch_only = 0
    num_prematch_only_correct = 0
    prematch_only_pairs = []

    num_correct_flip = 0
    num_incorrect_flip = 0
    num_correct_no_flip = 0
    num_incorrect_no_flip = 0

    match_correct_flip = []
    match_incorrect_flip = []
    match_correct_no_flip = []
    match_incorrect_no_flip = []

    for entry in result:
        if not entry["match_results"]:
            num_prematch_only += 1
            prematch_only_pairs.append(entry)
            label = entry["label"] 
            final_pred = entry["final_pred"]
            if (label == 0 and "no" in final_pred.lower()) or (label == 1 and "yes" in final_pred.lower()):
                num_prematch_only_correct += 1
        else:
            label = entry["label"] 
            final_pred = entry["final_pred"]
            prematch_pred = entry["prematch_results"]["pred"]
            match_pred = entry["match_results"]["pred"]
            correct_flip_0 = (label == 0 and "yes" in prematch_pred.lower() and "no" in match_pred.lower())
            correct_flip_1 = (label == 1 and "no" in prematch_pred.lower() and "yes" in match_pred.lower())
            incorrect_flip_0 = (label == 0 and "no" in prematch_pred.lower() and "yes" in match_pred.lower())
            incorrect_flip_1 = (label == 1 and "yes" in prematch_pred.lower() and "no" in match_pred.lower())
            correct_no_flip_0 = (label == 0 and "no" in prematch_pred.lower() and "no" in match_pred.lower())
            correct_no_flip_1 = (label == 1 and "yes" in prematch_pred.lower() and "yes" in match_pred.lower())
            incorrect_no_flip_0 = (label == 1 and "no" in prematch_pred.lower() and "no" in match_pred.lower())
            incorrect_no_flip_1 = (label == 0 and "yes" in prematch_pred.lower() and "yes" in match_pred.lower())
    
            if correct_flip_0 or correct_flip_1:
                num_correct_flip += 1
                match_correct_flip.append(entry)
            elif incorrect_flip_0 or incorrect_flip_1:
                num_incorrect_flip += 1
                match_incorrect_flip.append(entry)
            elif correct_no_flip_0 or correct_no_flip_1:
                num_correct_no_flip += 1
                match_correct_no_flip.append(entry)
            elif incorrect_no_flip_0 or incorrect_no_flip_1:
                num_incorrect_no_flip += 1
                match_incorrect_no_flip.append(entry)
            else:
                print("Invalid entry")

    stat = {
        "total_pairs": total_pairs,
        "prematch_stats": prematch_stats,
        "match_stats": match_stats,
        "prematch_stage": {
            "num_total": num_prematch_only, 
            "num_correct": num_prematch_only_correct, 
            },
        "match_stage":{
            "num_total": total_pairs - num_prematch_only, 
            "num_correct": num_correct_flip + num_correct_no_flip,
            "num_correct_flip": num_correct_flip, 
            "num_incorrect_flip": num_incorrect_flip, 
            "num_correct_no_flip": num_correct_no_flip, 
            "num_incorrect_no_flip": num_incorrect_no_flip
        }
    }
    result_analysis = {
        "stat": stat,
        "result": {
            "prematch_final": prematch_only_pairs,
            "match_correct_flip": match_correct_flip,
            "match_incorrect_flip": match_incorrect_flip, 
            "match_correct_no_flip": match_correct_no_flip, 
            "match_incorrect_no_flip": match_incorrect_no_flip
        }
    }
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_filename = f"analysis-{dataset}-{timestamp}.json"
    output_path = os.path.join("examples", "cascade", "output", dataset)
    output_filepath = os.path.join(output_path, output_filename)
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, "w") as json_file:
        json.dump(result_analysis, json_file, indent=4)
    
    print(f"Comparison results saved to {output_filepath}")


def sensitivity_analysis(args, dataset, thresholds, prematch_model="gpt-4o-mini", match_model="gpt-4o", num_pairs=2):
    f1_scores = []
    costs = []

    for threshold in thresholds:
        results_data = online(
            args=args,
            dataset=dataset,
            prematch_model=prematch_model,
            match_model=match_model,
            num_pairs=num_pairs,
            threshold=threshold
        )
        cascade_stats, prematch_single, match_single = generate_stats(results_data)

        f1_scores.append(cascade_stats['stats']['f1'])
        costs.append(cascade_stats['stats']['tokens']['cost'])

        print(f"Threshold: {threshold:.1f}, F1 Score: {cascade_stats['stats']['f1']:.4f}, Cost: {cascade_stats['stats']['tokens']['cost']:.2f}")

    return f1_scores, costs


def confidence_cost_plot(thresholds, costs):
    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, costs, marker='s', linestyle='-', color='red', label='Cost')
    plt.title('Confidence Threshold vs. Cost')
    plt.xlabel('Confidence Threshold')
    plt.ylabel('Cost')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

    output_path = os.path.join("examples", "cascade", "output")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_name = f"sensitivity-confidence-over-cost-{timestamp}.png"
    file_path = os.path.join(output_path, file_name)
    plt.savefig(file_path)


def confidence_f1_plot(thresholds, f1):
    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, f1, marker='s', linestyle='-', color='red', label='F1')
    plt.title('Confidence Threshold vs. F1')
    plt.xlabel('Confidence Threshold')
    plt.ylabel('F1')
    plt.ylim(0, 1.05) 
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

    output_path = os.path.join("examples", "cascade", "output")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_name = f"sensitivity-confidence-over-f1-{timestamp}.png"
    file_path = os.path.join(output_path, file_name)
    plt.savefig(file_path)
