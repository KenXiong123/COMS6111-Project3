import sys
import csv
from collections import defaultdict
from itertools import combinations, chain


def main():
    file_name = sys.argv[1]
    min_sup = sys.argv[2]
    min_conf = sys.argv[3]
    with open(file_name, 'r') as input_file, open('example-run.txt', 'a') as output_file:
        data = list(csv.reader(input_file))
        freq_itemsets = get_freq_itemsets(data, float(min_sup))
        rules = generate_rules(data, freq_itemsets, float(min_sup), float(min_conf))
        for rule in rules:
            output_file.write(rule[0])


def get_freq_itemsets(data, min_sup):
    # Count the support of each item in the transactions
    item_counts = defaultdict(int)
    for transaction in data:
        for item in transaction:
            item_counts[item] += 1

    # Filter out items that don't meet the minimum support threshold
    frequent_items = set(item for item, count in item_counts.items() if count / len(data) >= min_sup)

    # Initialize the list of frequent itemsets
    frequent_itemsets = [frozenset([item]) for item in frequent_items]
    result = {frozenset([item]): item_counts[item] for item in frequent_items}

    k = 2
    while True:
        # Generate candidate itemsets
        candidate_itemsets = set()
        for itemset1, itemset2 in combinations(frequent_itemsets, 2):
            candidate_itemset = itemset1.union(itemset2)
            if len(candidate_itemset) == k and candidate_itemset not in candidate_itemsets:
                candidate_itemsets.add(candidate_itemset)

        # Count the support of each candidate itemset in the transactions
        itemset_counts = defaultdict(int)
        for transaction in data:
            for itemset in candidate_itemsets:
                if itemset.issubset(transaction):
                    itemset_counts[itemset] += 1

        # Filter out candidate itemsets that don't meet the minimum support threshold
        frequent_itemsets = set(itemset for itemset, count in itemset_counts.items() if count / len(data) >= min_sup)
        result.update({itemset: itemset_counts[itemset] for itemset in frequent_itemsets})

        # Exit the loop if no more frequent itemsets are found
        if not frequent_itemsets:
            break

        k += 1

    return result


def generate_rules(data, freq_itemsets, min_sup, min_conf):
    # Define the powerset function
    def powerset(s):
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

    # Initialize an empty list to store the generated rules
    rules = []

    # Iterate over the frequent itemsets and generate rules
    for itemset in freq_itemsets:
        if len(itemset) > 1:
            # Generate all possible subsets of the itemset
            subsets = [frozenset(subset) for subset in powerset(itemset)]
            for subset in subsets:
                if subset and itemset - subset:
                    # Calculate the support and confidence of the rule
                    support = freq_itemsets[itemset] / len(data)
                    confidence = freq_itemsets[itemset] / freq_itemsets[subset]
                    # If the confidence and support are greater than the minimum values, print the rule
                    if confidence >= min_conf and support >= min_sup:
                        rule = f"{list(subset)} => {list(itemset - subset)} (Conf: {round(confidence * 100, 2)}%, Supp: {round(support * 100, 2)}%)\n"
                        tup = (rule, confidence)
                        rules.append(tup)
    rules = sorted(rules, key=lambda x: x[1], reverse=True)
    return rules


if __name__ == '__main__':
    main()
