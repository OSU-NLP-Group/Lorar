import re
import collections
import string

# copy from https://github.com/wenhuchen/OTT-QA/blob/master/evaluate_script.py


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_articles(text):
        regex = re.compile(r"\b(a|an|the)\b", re.UNICODE)
        return re.sub(regex, " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def get_tokens(s):
    if not s:
        return []
    return normalize_answer(s).split()


def compute_exact(a_gold, a_pred):
    return int(normalize_answer(a_gold) == normalize_answer(a_pred))


def compute_f1(a_gold, a_pred):
    gold_toks = get_tokens(a_gold)
    pred_toks = get_tokens(a_pred)
    common = collections.Counter(gold_toks) & collections.Counter(pred_toks)
    num_same = sum(common.values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        # If either is no-answer, then F1 is 1 if they agree, 0 otherwise
        return int(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(pred_toks)
    recall = 1.0 * num_same / len(gold_toks)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


class EvaluateTool(object):

    def __init__(self, args):
        self.args = args

    def evaluate(self, preds, golds, section):
        summary = {}
        exact_scores = {}
        f1_scores = {}
        for pred, gold in zip(preds, golds):
            qas_id = gold['id']
            gold_answers = [gold['answer_text']]

            exact_scores[qas_id] = max(compute_exact(a, pred) for a in gold_answers)
            f1_scores[qas_id] = max(compute_f1(a, pred) for a in gold_answers)
        total = len(golds)
        qid_list = list(exact_scores.keys())

        summary["exact"] = sum(exact_scores[k] for k in qid_list) / total
        summary["f1"] = sum(f1_scores[k] for k in qid_list) / total

        return summary