from nltk.tokenize import regexp_tokenize
import numpy as np
from collections import Counter, defaultdict
import math

# Here is a default pattern for tokenization; you can substitute it with yours
default_pattern =  r"""(?x)                  
                        (?:[A-Z]\.)+          
                        |\$?\d+(?:\.\d+)?%?    
                        |\w+(?:[-']\w+)*      
                        |\.\.\.               
                        |(?:[.,;"'?():-_`])    
                    """

def tokenize(text, pattern = default_pattern):
    """Tokenize senten with specific pattern
    
    Arguments:
        text {str} -- sentence to be tokenized, such as "I love NLP"
    
    Keyword Arguments:
        pattern {str} -- reg-expression pattern for tokenizer (default: {default_pattern})
    
    Returns:
        list -- list of tokenized words, such as ['I', 'love', 'nlp']
    """
    text = text.lower()
    return regexp_tokenize(text, pattern)


class FeatureExtractor(object):
    """Base class for feature extraction.
    """
    def __init__(self):
        pass
    def fit(self, text_set):
        pass
    def transform(self, text):
        pass  
    def transform_list(self, text_set):
        pass



class UnigramFeature():
    """Example code for unigram feature extraction
    """
    def __init__(self):
        self.unigram_counts = {}
    
    def fit(self, text_set):

        all_words = [word for text in text_set for word in text]
        self.total_words = len(all_words)
        self.total_sentences = len(text_set)

        self.word_freq = Counter(all_words)

        for sentence in text_set:
            for word in sentence:
                if self.word_freq[word] < 3:
                    if '<UNK>' in self.unigram_counts:
                        self.unigram_counts['<UNK>'] += self.word_freq[word]
                    else:
                        self.unigram_counts['<UNK>'] = self.word_freq[word]
                else:
                    self.unigram_counts[word] = self.word_freq[word]
        
        self.unigram_counts['<STOP>'] = len(text_set)
        
        print(len(self.unigram_counts))
        return self.unigram_counts
    
    def MLE(self):
        """Calculate Maximum Likelihood Estimation for unigram model with additive smoothing."""
        vocab_size = len(self.unigram_counts)
        self.unigram_prob = {word: (count + 1) / (self.total_words + vocab_size) for word, count in self.unigram_counts.items()}
        for word in self.unigram_prob:
            if (word == '<UNK>') or (word == '<STOP>'):
                print(word, self.unigram_prob[word])
        return self.unigram_prob
    
    def perplexity(self, text_set):
        log_sum = 0
        unigram_prob = self.MLE()
        total_test_tokens = sum(len(sentence) + 1 for sentence in text_set)

        for sentence in text_set:
            for word in sentence:
                if word in self.unigram_prob:
                    log_sum += math.log2(unigram_prob[word])
                if word not in self.unigram_prob:
                    log_sum += math.log2(self.unigram_prob['<UNK>'])

        log_sum += math.log2(unigram_prob['<STOP>'])

        return 2 ** (-log_sum / total_test_tokens)


class BigramFeature(FeatureExtractor):
    """Bigram feature extractor analogous to the unigram one.
    """
    def __init__(self):
        # Add your code here!
        self.bigram_counts = {}
        self.unigram_counts = {}
        self.vocab = set()

    def fit(self, text_set: list):
        self.data = text_set

        word_counts = Counter([word for sentence in self.data for word in sentence])
        self.vocab = {word if count >= 3 else '<UNK>' for word, count in word_counts.items()}
        processed_data = [[word if word in self.vocab else '<UNK>' for word in sentence] + ['<STOP>']
            for sentence in self.data
        ]
        
        for sentence in processed_data:
            for i in range(len(sentence) - 1):
                bigram = (sentence[i], sentence[i + 1])
                if bigram not in self.bigram_counts:
                    self.bigram_counts[bigram] = 1
                else:
                    self.bigram_counts[bigram] += 1
                if bigram[0] not in self.unigram_counts:
                    self.unigram_counts[bigram[0]] = 1
                else:
                    self.unigram_counts[bigram[0]] += 1
        return self.bigram_counts

    def MLE(self, bigram):
        """Calculate MLE probability for a bigram with additive smoothing."""
        context = bigram[0]
        vocab_size = len(self.vocab)
        bigram_count = self.bigram_counts.get(bigram, 0)
        unigram_count = self.unigram_counts.get(context, 0)
        return (bigram_count + 1) / (unigram_count + vocab_size)
    
    def perplexity(self, test_data):
        """Calculate perplexity on test data."""
        processed_data = [[word if word in self.vocab else '<UNK>' for word in sentence] + ['<STOP>']
            for sentence in test_data
        ]
        log_prob_sum = 0
        token_count = 0
        
        for sentence in processed_data:
            for i in range(len(sentence) - 1):
                bigram = (sentence[i], sentence[i + 1])
                prob = self.MLE(bigram)
                if prob > 0:
                    log_prob_sum += math.log2(prob)
                token_count += 1
        
        return 2 ** (-log_prob_sum / token_count)
        
class Trigram(FeatureExtractor):
    def __init__(self):
        self.trigram = {}
        self.trigram_counts = {}
        self.bigram_counts = {}
        self.vocab = set()
        # self.stopwords = [
        #     "a", "about", "above", "after", "again", "against", "all", "also", "am", "an", "and", "any", "are", "aren't", "as", "at",
        #     "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", 
        #     "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", 
        #     "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", 
        #     "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", 
        #     "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", 
        #     "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", 
        #     "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", 
        #     "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
        #     "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", 
        #     "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
        #     "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", 
        #     "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", 
        #     "you're", "you've", "your", "yours", "yourself", "yourselves"
        # ]

        
    def fit(self, text_set: list):
        self.data = text_set
        word_counts = Counter([word for sentence in self.data for word in sentence])
        self.vocab = {word if count >= 3 else '<UNK>' for word, count in word_counts.items()}
        processed_data = [[word if word in self.vocab else '<UNK>' for word in sentence] + ['<STOP>'] for sentence in self.data
        ]
        
        for sentence in processed_data:
            for i in range(len(sentence) - 2):
                trigram = (sentence[i], sentence[i + 1], sentence[i + 2])
                bigram = (sentence[i], sentence[i + 1])
                if trigram not in self.trigram_counts:
                    self.trigram_counts[trigram] = 1
                else:
                    self.trigram_counts[trigram] += 1
                if bigram not in self.bigram_counts:
                    self.bigram_counts[bigram] = 1
                else:
                    self.bigram_counts[bigram] += 1
        return self.trigram_counts

    def MLE(self, trigram):
        """Calculate MLE probability for a trigram with additive smoothing."""
        context = trigram[:2]
        vocab_size = len(self.vocab)
        trigram_count = self.trigram_counts.get(trigram, 0)
        bigram_count = self.bigram_counts.get(context, 0)
        return (trigram_count + 1) / (bigram_count + vocab_size)
    
    def perplexity(self, test_data):
        """Calculate perplexity on test data."""
        processed_data = [[word if word in self.vocab else '<UNK>' for word in sentence] + ['<STOP>']
            for sentence in test_data
        ]
        log_prob_sum = 0
        token_count = 0
        
        for sentence in processed_data:
            for i in range(2, len(sentence)):
                trigram = (sentence[i - 2], sentence[i - 1], sentence[i])
                prob = self.MLE(trigram)
                if prob > 0:
                    log_prob_sum += math.log2(prob)
                token_count += 1
        
        return 2 ** (-log_prob_sum / token_count)
