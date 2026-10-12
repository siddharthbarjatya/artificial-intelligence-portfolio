tokenize <- function(text) {
  # Replace punctuation and non-alphanumeric with space
  text <- gsub("[^a-z0-9[:space:]]", " ", text)
  # Split into words
  tokens <- unlist(strsplit(text, "\\s+"))
  # Remove empty tokens
  tokens <- tokens[trimws(tokens) != ""]
  return(tokens)
}

parse_wsj <- function(lines, output_file) {
  # Lowercase and strip tags first
  lines <- tolower(lines)
  lines <- gsub("<[^>]+>", " ", lines)
  lines <- trimws(lines)

  doc_text <- ""           # Accumulate text
  docno <- NULL            # Store current DOCNO
  out_conn <- file(output_file, open = "wt")

  for (i in seq_along(lines)) {
    line <- lines[i]

    # Skip empty lines
    if (line == "") next

    # Check if line looks like a WSJ ID (e.g., wsj900101-0001)
    if (grepl("wsj\\d{6}-\\d{4}", line)) {

      # If a document in progress, save it before starting new one
      if (!is.null(docno)) {
        writeLines(docno, out_conn)
        tokens <- tokenize(doc_text)
        # Filter out the docno if it got into the text
        tokens <- tokens[tokens != docno]
        writeLines(tokens, out_conn)
        writeLines("", out_conn) # Blank line separator
      }

      # Reset for the new document
      docno <- trimws(line)
      doc_text <- ""
      cat(sprintf("Processing: %s (%.1f%%)\n", docno, (i / length(lines)) * 100))

    } else {
      # Accumulate text for the current document
      doc_text <- paste(doc_text, line)
    }
  }

  # Write the final document after loop finishes
  if (!is.null(docno)) {
    writeLines(docno, out_conn)
    tokens <- tokenize(doc_text)
    writeLines(tokens, out_conn)
  }

  close(out_conn)
  cat("Parsing complete. Output written to", output_file, "\n")
}

wsjxml <- readLines("wsj.xml", warn = FALSE)
parse_wsj(wsjxml, "wsj_parsed.txt")
