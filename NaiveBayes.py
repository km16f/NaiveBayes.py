import os
import sys
import json

if len(sys.argv) == 3:
    train_file = sys.argv[1]
    test_file = sys.argv[2]
elif len(sys.argv) > 3:
    train_file = sys.argv[1]
    test_file = sys.argv[2]
    print ("Error: Too Many Arguments")
    exit()
elif len(sys.argv) < 3:
    print("Error: Missing Argument")
    exit()


def read_in_values(filepath):
    pos = [{}]
    neg = [{}]
    pos_sum = {}
    neg_sum = {}
    pos_num = 0
    neg_num = 0
    attr_list = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        largest_index, largest_value = find_largest_index(lines)
        pos_sum = initialize_dict(pos_sum, largest_index, largest_value)
        neg_sum = initialize_dict(neg_sum, largest_index, largest_value)
        for line in lines:
            attr_list[:] = []
            s = line.split(' ')
            data = {}
            if s[0] == '+1':
                pos_num += 1
                for entry in s[1:]:
                    sp = entry.split(':')
                    key = sp[0]
                    attr_list.append(key)
                    val = sp[1].strip()
                    pos_sum[key][val] += 1
                for i in range(1 ,largest_index + 1):
                    if str(i) not in attr_list:
                        pos_sum[str(i)]['0'] += 1
            else:
                neg_num += 1
                for entry in s[1:]:
                    sp = entry.split(':')
                    key = sp[0]
                    attr_list.append(key)
                    val = sp[1].strip()
                    neg_sum[key][val] += 1
                for i in range(1, largest_index + 1):
                    if str(i) not in attr_list:
                        neg_sum[str(i)]['0'] += 1
    with open ("pos_json.json", 'w+') as pos_write:
        json.dump(pos_sum, pos_write, indent=4)
    with open ("neg_json.json", "w+") as neg_write:
        json.dump(neg_sum, neg_write, indent=4)
    return pos_sum, neg_sum, pos_num, neg_num, largest_index


def initialize_dict(dictionary, largest_index, largest_value):
    for i in range(1, largest_index + 1):
        dictionary[str(i)] = {}
        for x in range(0, largest_value + 1):
            dictionary[str(i)][str(x)] = 0
    return dictionary


def find_largest_index(lines):
    largest_index = 1
    largest_value = 0
    for line in lines:
        s = line.split(' ')
        for pair in s:
            if pair == '-1' or pair == '+1':
                pass
            else:
                sp = pair.split(':')
                if int(sp[0]) > largest_index:
                    largest_index = int(sp[0])
                if int(sp[1]) > largest_value:
                    largest_value = int(sp[1])
    return largest_index, largest_value


def get_probability(key, value, class_dict, count):
    return class_dict[key][value]/count


def get_missing(line, largest_index):
    attribute_list = []
    zero_list = []
    s = line.split(' ')
    for entry in s[1:]:
        sp = entry.split(':')
        attribute_list.append(sp[0])
    for i in range(1, largest_index + 1):
        if str(i) not in attribute_list:
            zero_list.append(str(i))
    return zero_list


def naive_bayes(line, pos_data, neg_data, pos_count, neg_count, largest_index):
    total_count = pos_count + neg_count
    pos_probability = pos_count / total_count
    neg_probability = neg_count / total_count

    pos_product = 1
    neg_product = 1

    zero = get_missing(line, largest_index)
    s = line.split(' ')
    for entry in s[1:]:
        sp = entry.split(':')
        pos_p = get_probability(sp[0], sp[1].strip(), pos_data, pos_count)
        neg_p = get_probability(sp[0], sp[1].strip(), neg_data ,neg_count)
        pos_product = pos_product * pos_p
        neg_product = neg_product * neg_p
    for entry in zero:
        pos_p = get_probability(entry, '0', pos_data, pos_count)
        neg_p = get_probability(entry, '0', neg_data, neg_count)
        pos_product = pos_product * pos_p
        neg_product = neg_product * neg_p
    final_pos = pos_product * pos_probability
    final_neg = neg_product * neg_probability
    if (final_pos == 0 or final_neg == 0):
        print ("UH OH SPONGEBOB")
    if final_pos > final_neg:
        return "+1"
    elif final_neg > final_pos:
        return "-1"


if __name__ == "__main__":
    true_pos = 0
    false_pos = 0
    true_neg = 0
    false_neg = 0
    pos_data, neg_data, pos_count, neg_count, largest_index = read_in_values(train_file)
    with open(train_file, 'r') as file_:
        lines = file_.readlines()
        for line in lines:
            s = line.split()
            actual_class = s[0]
            r = naive_bayes(line, pos_data, neg_data, pos_count, neg_count, largest_index)
            if r == '+1' and r == actual_class:
                true_pos += 1
            elif r == '+1' and r != actual_class:
                false_pos += 1
            elif r == '-1' and r == actual_class:
                true_neg += 1
            elif r == '-1' and r != actual_class:
                false_neg += 1
    print("True Pos: %s" % true_pos)
    print("False Pos: %s" % false_pos)
    print("True Neg: %s" % true_neg)
    print("False Neg: %s" % false_neg)