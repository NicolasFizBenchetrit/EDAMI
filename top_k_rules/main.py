from rule_list import rule_list
from rule_list import rule
import custom_twitter_api
import time

def populate_rule_list_with_simple_rules(rules, sequences):
    for i in range(len(sequences)):
        seq = sequences[i]
        for x in range(len(seq)):
            for y in range(x+1, len(seq)):
                new_rule = rule([seq[x]], [seq[y]])
                # check that the rule is valid an add it to the list
                if new_rule.x != new_rule.y:
                    new_rule.sequence_indexes.append(i)
                    rules.add(new_rule)

def get_tweet_text(word):
    tweet_text = []
    tweets = custom_twitter_api.search_tweets(word, '30')
    for tweet in tweets:
        tweet_text.append(tweet.text)
    return tweet_text

def main():
    SEQUENCES = []
    WORDS = ['cpp', 'java', 'python', 'c#', 'c', 'php', 'haskel']

    for word in WORDS:
        tmp = get_tweet_text(word)
        for t in tmp:
            SEQUENCES.append(t)

    rules = rule_list()
    start = time.time()

    populate_rule_list_with_simple_rules(rules, SEQUENCES)
    rules.filter_top_k(SEQUENCES)
    rules.expand_x(SEQUENCES)
    rules.expand_y(SEQUENCES)

    print("Execution time: " + str(time.time() - start))
    print("SEQUENCES size: " + str(len(SEQUENCES)))
    print("Max support: " + str(rules.max_support()))
    print("Max confidence: " + str(rules.max_confidence()))
    print("Average support: " + str(rules.average_support()))
    print("Average confidence " + str(rules.average_confidence()))

if __name__ == "__main__":
    main()
