from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
import os

class TextProcessor:
    def __init__(self, input_data, is_file=True):
        self.is_file = is_file
        if self.is_file:
            if not os.path.exists(input_data):
                raise FileNotFoundError(f"File not found: {input_data}")
            with open(input_data, 'r') as f:
                self.text = f.read()
        else:
            self.text = input_data

    def summarize_text(self, max_sentences=10, max_len_sentence=30, remove_duplicates=True):
        sentences = sent_tokenize(self.text.strip())
        cleaned_sentences = [sen.strip() for sen in sentences if sen.strip()]
        word_counts = Counter(word.lower() for word in word_tokenize(self.text) if word.isalnum())
        def sentence_score(sentence, word_counts=word_counts):
            words = word_tokenize(sentence)
            uniq_score = sum(1 / (count + 1) for word, count in word_counts.items() if word in words)
            concise_score = 1 / (len(words) + 1)
            clarity_score = sum(1 if word in word_counts.keys() else 0 for word in words)
            return uniq_score * concise_score * clarity_score
        sentence_scores = {sentence: sentence_score(sentence) for sentence in cleaned_sentences}
        sorted_sentences = sorted(sentence_scores.items(), key=lambda item: item[1], reverse=True)
        summarized_sentences = []
        seen_sentences = set()  # Track seen sentences to avoid redundancy
        for sentence, score in sorted_sentences:
            if not remove_duplicates or sentence.lower() not in seen_sentences:
                summarized_sentences.append(sentence)
                seen_sentences.add(sentence.lower())
            if len(summarized_sentences) >= max_sentences:
                break
        return ' '.join(summarized_sentences)

    def remove_long_lines(self, max_len=5000):
        lines = self.text.split('\n')
        short_lines = [line for line in lines if len(line) <= max_len]
        return '\n'.join(short_lines)

    def remove_duplicate_lines(self):
        lines = self.text.split('\n')
        seen_lines = set()
        unique_lines = []
        for line in lines:
            if line not in seen_lines:
                unique_lines.append(line)
                seen_lines.add(line)
        return '\n'.join(unique_lines)
