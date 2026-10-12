library(data.table)

# Pre-processing
lines <- scan("wsj_parsed.txt", what = "", sep = "\n", quiet = TRUE)
is_doc <- grepl("wsj\\d{6}-\\d{4}", lines)
doc_id <- cumsum(is_doc)
docno <- lines[is_doc]
words <- lines[!is_doc]
doc_id_words <- doc_id[!is_doc]

dt <- data.table(word = words, doc = doc_id_words)
tf_dt <- dt[, .N, by = .(word, doc)]
setnames(tf_dt, "N", "tf")

doc_len <- dt[, .N, by = doc]
setnames(doc_len, "N", "len")

N_docs <- length(docno)
df_dt <- tf_dt[, .N, by = word]
setnames(df_dt, "N", "df")
df_dt[, idf := log(N_docs / df)]

# Binary File Generation
# sort the vocabulary to make binary search possible later
setorder(df_dt, word)
setorder(tf_dt, word, doc)

# Open file connections
f_postings <- file("postings.bin", "wb")
f_vocab    <- file("vocab.bin", "wb")

# Data structures to hold metadata
offsets <- numeric(nrow(df_dt))
lengths <- numeric(nrow(df_dt)) # length in bytes for the posting block

current_pos <- 0

cat("Writing binary index...\n")

for (i in 1:nrow(df_dt)) {
  target_word <- df_dt$word[i]

  # Filter tf_dt for this specific word's postings
  word_postings <- tf_dt[word == target_word]

  # Metadata for the vocab file
  offsets[i] <- current_pos

  # Write DocIDs (integer, 4 bytes each) and TFs (integer, 4 bytes each)
  # Format: [DocID1, TF1, DocID2, TF2, ...]
  postings_vector <- as.vector(rbind(word_postings$doc, word_postings$tf))
  writeBin(as.integer(postings_vector), f_postings)

  # Calculate bytes written (2 integers per doc * 4 bytes each)
  bytes_written <- nrow(word_postings) * 2 * 4
  lengths[i] <- bytes_written
  current_pos <- current_pos + bytes_written
}

close(f_postings)

# Save Vocabulary and Metadata
vocab_meta <- data.table(
  word   = df_dt$word,
  idf    = df_dt$idf,
  offset = offsets,
  size   = lengths
)

# Save the metadata and document info (final search engine rankings)
saveRDS(vocab_meta, "vocab_metadata.rds")
saveRDS(docno, "docno.rds")
saveRDS(doc_len$len, "doc_lengths.bin")
