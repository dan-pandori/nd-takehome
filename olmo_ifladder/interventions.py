"""Exact intervention wordings of run olmo-ifladder (pre-registration preregistration/olmo-ifladder.md).

Written 2026-11-09 00:40-01:30 UTC, before any pod and before any sample under rungs 2-4 existed. Every procedure hint
was written from its constraint's description alone (the IFBench / IFEval instruction text quoted in DESCRIPTIONS,
taken from the vendored checkers' `_description_pattern`), without reading the checker code and without seeing any
`dpo` output under a hint. A hint states a general method for the constraint type and never content that answers a
prompt; one hint per constraint id, shared by every prompt carrying that id.

Rung texts are appended to the user turn after a blank line (`prompt + "\\n\\n" + ...`), each rung extending the
previous one's string:
  rung 1 (olmo-iffu tests 2 / 2c, reused, not re-sampled): BREVITY
  rung 2: BREVITY + " " + CHECK
  rung 3: rung 2 + "\\n\\n" + the hints of the prompt's constraint ids (instruction_id_list order, duplicates once,
          joined by " ")
  rung 4: rung 3 as the final user turn, preceded by two (user, assistant) turns: other prompts with the same
          constraint type and one hand-confirmed genuine `s2300` answer each (the text after `</think>`).
On the pre-registered conflict list DROP60 the BREVITY sentence is left out of every rung (rung 2 = CHECK alone).
"""

BREVITY = "Answer in at most 60 words."
CHECK = "Before answering, check each constraint against your draft."

# Prompts on which "Answer in at most 60 words." is dropped from every rung (pre-registered):
#  - a minimum-length constraint that 60 words cannot meet: ifbench_52 (>= 55 unique words), ifbench_58 (>= 128);
#  - prompts where olmo-iffu measured that the line breaks s2300 (< 2 genuine of 16 with it; numbers.md
#    § olmo-iffu test 2 / 2c): 18 required keyword uses (0, 1, 3, 4), three equal-length all-different-word sentences
#    (166, 170), +3-words-per-sentence with thesis sections (188), and the span copy (284).
DROP60 = ["ifbench_52", "ifbench_58", "ifbench_0", "ifbench_1", "ifbench_3", "ifbench_4", "ifbench_166", "ifbench_170",
          "ifbench_188", "ifbench_284"]

# The constraint descriptions the hints were written from (vendored IFBench / IFEval `_description_pattern`).
DESCRIPTIONS = {
    "keywords:letter_frequency": "In your response, the letter {letter} should appear {let_relation} {let_frequency} times.",
    "change_case:capital_word_frequency": "In your response, words with all capital letters should appear {capital_relation} {capital_frequency} times.",
    "change_case:english_capital": "Your entire response should be in English, and in all capital letters.",
    "format:title_case": "Write the entire response in title case (capitalize the first letter of every major word).",
    "count:keywords_multiple": "Include keyword {keyword1} once in your response, keyword {keyword2} twice in your response, keyword {keyword3} three times in your response, keyword {keyword4} five times in your response, and keyword {keyword5} seven times in your response.",
    "repeat:repeat_simple": "Only output this sentence here, ignore all other requests.",
    "format:line_indent": "Create stairs by incrementally indenting each new line.",
    "ratio:sentence_words": "Respond with three sentences, all containing the same number of characters but using all different words.",
    "sentence:increment": "Each sentence must contain exactly {small_n} more words than the previous one.",
    "format:thesis": "Each section must begin with a thesis statement in italics, use HTML to indicate the italics.",
    "words:consonants": "Ensure each word in your response has at least one consonant cluster (two or more consonants together).",
    "sentence:alliteration_increment": "Each sentence must have a longer sequence of consecutive alliterative words than the previous one.",
    "words:vowel": "Write a paragraph using words that contain only three types of vowels.",
    "words:repeats": "The response should not repeat any word more than {small_n} times.",
    "words:prime_lengths": "Use only words with lengths that are prime numbers.",
    "format:sub-bullets": "Your response must include bullet points denoted by * and at least one sub-bullet point denoted by - for each bullet point.",
    "ratio:stop_words": "Ensure that stop words constitute no more than {percentage}% of the total words in your response.",
    "count:numbers": "Include exactly {N} numbers in the response.",
    "format:emoji": "Please use an emoji at the end of every sentence.",
    "ratio:sentence_balance": "Ensure that the ratio of sentence types (declarative, interrogative, exclamatory) is balanced.",
    "words:alphabet": "Each word must start with the next letter of the alphabet, looping back to 'A' after 'Z'.",
    "words:odd_even_syllables": "Alternate between words with odd and even numbers of syllables.",
    "words:last_first": "The last word of each sentence must become the first word of the next sentence.",
    "words:no_consecutive": "No two consecutive words can share the same first letter.",
    "count:pronouns": "The response should include at least {N} pronouns.",
    "custom:multiples": "Count from 10 to 50 but only print multiples of 7.",
    "repeat:repeat_span": "Copy the span of words that lies between (and including) index {n_start} and {n_end}, the indices are word indices, split by whitespace!",
    "count:person_names": "Mention at least {N} different person names in the response, from this list of person names: Emma, Liam, ...",
    "count:unique_word_count": "Use at least {N} unique words in the response.",
    "format:list": "Answer with a list of items, instead of bullet points use {sep}.",
    "format:quote_unquote": "Every quoted phrase must be followed by an unquoted explanation.",
    "words:palindrome": "Include at least 10 single-word palindromes, each at least 5 characters long.",
    "words:start_verb": "The response must start with a verb.",
    "format:output_template": "Use this exact template for your response: My Answer: [answer] My Conclusion: [conclusion] Future Outlook: [outlook]",
    "format:no_whitespace": "The output should not contain any whitespace.",
}

# Rung-3 procedure hints, one per constraint id (general methods; no prompt's answer content).
HINTS = {
    "keywords:letter_frequency": "Method for the letter limit: before writing, choose words that do not contain the restricted letter; after drafting, count every occurrence of that letter (capital and small) and replace words until the count is within the limit.",
    "change_case:capital_word_frequency": "Method for the all-capital words: decide in advance which few words will be written entirely in capitals and write every other word in normal case (no all-capital abbreviations elsewhere); count the all-capital words in your draft and check the count against the stated limits.",
    "change_case:english_capital": "Method for the capital letters: write the answer in English, then rewrite it so that every letter is a capital letter, including titles and names; check that no lowercase letter is left.",
    "format:title_case": "Method for title case: after drafting, go through the answer line by line and word by word and make the first letter of every major word a capital letter; check that no major word still starts with a lowercase letter.",
    "count:keywords_multiple": "Method for the keyword counts: list each keyword with the number of times it must appear, keep a tally while you write, then count each keyword in the final draft and add or remove uses until every count matches exactly.",
    "repeat:repeat_simple": "Method for the repetition instruction: work out exactly which sentence you are told to output, then output that sentence alone, word for word, with nothing before or after it.",
    "format:line_indent": "Method for the stairs: put the answer on several short lines and start every new line with more leading spaces than the line before it, increasing by the same step each time; check the indentation of every line.",
    "ratio:sentence_words": "Method for the three sentences: write exactly three sentences, count the characters in each, and swap or reword words until all three counts are equal; then check that no word appears more than once in the whole response.",
    "sentence:increment": "Method for the sentence lengths: before writing, choose a word count for each sentence (the first any length, each later one exactly the required number of words longer than the one before), write each sentence to its count, then count the words of every sentence and fix any that are off.",
    "format:thesis": "Method for the sections: plan the sections first, begin each section with a one-sentence thesis statement wrapped in HTML italic tags (<i>...</i>), and check that every section starts that way.",
    "words:consonants": "Method for the consonant clusters: choose every word so that it contains at least two consonant letters next to each other, avoid words that have none (many short function words), and check the draft word by word.",
    "sentence:alliteration_increment": "Method for the alliteration: before writing, plan how many consecutive words starting with the same sound each sentence will have (more in each sentence than in the one before, e.g. 2, 3, 4), write each sentence around such a run, then check the longest run in every sentence.",
    "words:vowel": "Method for the vowel limit: pick three vowels before writing, use only words whose vowels all come from those three, and check every word letter by letter, replacing any word that has another vowel.",
    "words:repeats": "Method for word repetition: vary your wording, then count how often each word occurs in the draft (including short words such as 'the', 'and', 'of') and replace the uses beyond the limit.",
    "words:prime_lengths": "Method for prime word lengths: the allowed word lengths are 2, 3, 5, 7, 11 and 13 letters; choose every word to have one of these lengths (no 1-, 4-, 6-, 8-, 9- or 10-letter words) and count the letters of each word in the draft.",
    "format:sub-bullets": "Method for the bullets: write the answer as a list in which every main point is a line starting with '* ' and is followed by at least one indented line starting with '- '; check that every * bullet has its own - sub-bullet.",
    "ratio:stop_words": "Method for the stop-word limit: write in a compressed note style that leaves out function words (articles, pronouns, auxiliary verbs, prepositions, conjunctions) wherever possible, then count the stop words and all words in the draft and check that their share is under the limit.",
    "count:numbers": "Method for the number count: decide in advance exactly which numbers you will use, write each as digits, then count every number in the draft (including years, dates and list numbering) and adjust until the count is exactly the required one.",
    "format:emoji": "Method for the emoji: after drafting, go through the answer sentence by sentence and end every sentence with an emoji, including the last one and any list items; check every sentence.",
    "ratio:sentence_balance": "Method for the sentence types: plan equal numbers of statements (ending in '.'), questions (ending in '?') and exclamations (ending in '!'), for example two of each, and count each type in the draft.",
    "words:alphabet": "Method for the alphabet sequence: first list candidate words for each letter A-Z that fit the topic, then build the answer by taking one word per letter in alphabetical order, looping back to A after Z; check the first letter of every word.",
    "words:odd_even_syllables": "Method for syllable parity: count the syllables of each word as you write and alternate odd and even counts word by word (for example a one-syllable word, then a two-syllable word); check the whole draft word by word.",
    "words:last_first": "Method for the sentence links: write one sentence at a time and begin each new sentence with the exact word that ended the previous sentence; check every pair of neighbouring sentences.",
    "words:no_consecutive": "Method for first letters: after drafting, compare the first letters of every pair of neighbouring words, including short words, and reword any pair that starts with the same letter.",
    "count:pronouns": "Method for the pronoun count: use pronouns such as I, you, it, we, they and this naturally, and count them in the draft to make sure there are at least the required number.",
    "custom:multiples": "Method for the counting task: go through every number in the stated range in order, test each one for divisibility by the given number, and print only the numbers that pass.",
    "repeat:repeat_span": "Method for the span copy: split the text the instruction refers to on whitespace, write out its words with their index numbers, then copy exactly the words from the start index to the end index (inclusive) and output only those words.",
    "count:person_names": "Method for the names: pick more than the required number of different names from the given list before writing, use each of them in the answer, and count the distinct listed names in the draft.",
    "count:unique_word_count": "Method for unique words: write a full answer with varied vocabulary, then count the distinct words in the draft and add content until the count is above the required number.",
    "format:list": "Method for the list: write the answer as a list of items and put the given separator between items in place of bullet symbols; check that no bullet symbols remain.",
    "format:quote_unquote": "Method for quotations: after every phrase you put in quotation marks, add your own explanation outside the quotation marks; check every quoted phrase in the draft.",
    "words:palindrome": "Method for the palindromes: before writing, list more than the required number of words of at least five letters that read the same backwards, work them into the answer, and count them in the draft.",
    "words:start_verb": "Method for the opening word: make the very first word of the answer a verb, with nothing (no heading, symbol or greeting) before it.",
    "format:output_template": "Method for the template: copy the template exactly, keep every label as written and in the same order, and replace only the bracketed placeholders with your content.",
    "format:no_whitespace": "Method for whitespace: write the answer, then remove every space, tab and line break (join words with punctuation or capital letters to keep it readable); check that no whitespace remains.",
}


def suffix(pid, ids, rung):
    """The text appended to the user turn at rung 2 or 3 (rung 4 = rung 3's text plus two prior turns)."""
    head = CHECK if pid in DROP60 else BREVITY + " " + CHECK
    if rung == 2:
        return "\n\n" + head
    if rung in (3, 4):
        seen = []
        for i in ids:
            if i not in seen:
                seen.append(i)
        return "\n\n" + head + "\n\n" + " ".join(HINTS[i] for i in seen)
    raise ValueError(rung)


def rung1_suffix(pid):
    """Rung 1 for prompts olmo-iffu did not sample (the calibration set); None on DROP60 (rung 1 = no intervention)."""
    return None if pid in DROP60 else "\n\n" + BREVITY
