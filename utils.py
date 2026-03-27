def get_bigrams(text):
    # Returns a set of bigrams for a given string.
    text = text.lower()
    return set(text[i:i+2] for i in range(len(text) - 1))

def jaccard_similarity(str1, str2):
    # Computes Jaccard Similarity between two strings based on bigrams.
    if not str1 or not str2:
        return 0.0
    
    set1 = get_bigrams(str1)
    set2 = get_bigrams(str2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0.0
        
    return intersection / union
