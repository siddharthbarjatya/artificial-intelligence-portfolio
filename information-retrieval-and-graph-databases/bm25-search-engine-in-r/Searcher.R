options(warn = -1)
library(data.table)
# Command line arguments: Rscript search.R input.in output.out
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("Usage: Rscript search.R <query_file.in> <output_file.out>")
}

input_file <- args[1]
output_file <- args[2]

# Load Metadata
vocab <- readRDS("vocab_metadata.rds")
docno_mapping <- readRDS("docno.rds")
doc_lengths   <- readRDS("doc_lengths.bin")
avg_doc_len   <- mean(doc_lengths)
N_docs        <- length(docno_mapping)

# Read Query
query_text <- readLines(input_file, warn = FALSE)
query_terms <- unique(unlist(strsplit(tolower(query_text), "\\s+")))
query_terms <- query_terms[query_terms != ""]

# Retrieval and Scoring (BM25)
# BM25 Parameters
k1 <- 1.2
b  <- 0.75

# Accumulator for document scores
# Initialize a sparse vector or a numeric vector of size N_docs
scores <- numeric(N_docs)
matched_docs_list <- list()

# Open the binary postings file
f_postings <- file("postings.bin", "rb")

for (term in query_terms) {
  meta <- vocab[word == term]

  if (nrow(meta) > 0) {
    # Seek and Read only the postings for this term
    seek(f_postings, where = meta$offset)
    raw_data <- readBin(f_postings, "integer", n = meta$size / 4)

    # Reshape: Odd indices are DocIDs, Even indices are TFs
    term_docs <- raw_data[seq(1, length(raw_data), by = 2)]
    term_tfs  <- raw_data[seq(2, length(raw_data), by = 2)]

    # Store doc lists for the AND condition logic
    matched_docs_list[[term]] <- term_docs

    # Calculate BM25 for each document containing the term
    # IDF is already stored in vocab metadata
    idf <- meta$idf

    # Vectorized BM25 calculation for this term
    current_lens <- doc_lengths[term_docs]
    term_scores <- idf * ((term_tfs * (k1 + 1)) / (term_tfs + k1 * (1 - b + b * (current_lens / avg_doc_len))))

    # Add to total scores
    scores[term_docs] <- scores[term_docs] + term_scores
  }
}
close(f_postings)

# Apply AND Logic
if (length(matched_docs_list) == length(query_terms)) {
  final_doc_ids <- Reduce(intersect, matched_docs_list)
} else {
  final_doc_ids <- integer(0) # One or more terms didn't exist
}

# Format and Save Results
if (length(final_doc_ids) > 0) {
  # Extract scores for the documents that passed the AND filter
  results <- data.table(
    docno = docno_mapping[final_doc_ids],
    rsv   = scores[final_doc_ids]
  )

  # Sort by RSV (Relevance Score Value) descending
  setorder(results, -rsv)

  # Write to .out file
  fwrite(results, output_file, sep = " ", col.names = FALSE)
} else {
  # Write empty file if no matches
  file.create(output_file)
}
