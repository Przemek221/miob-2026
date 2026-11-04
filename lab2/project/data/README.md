# Prepared SpamAssassin data

One row is one email. `text` contains its decoded subject and complete plain-text body; `label` is the corpus label (`ham` or `spam`). `message_id` links predictions to the message. Neither ID nor label is a feature. The model reads only the six numeric columns listed below; it does not directly read the email text.

| Feature | Definition |
|---|---|
| `free_rate`, `money_rate`, `remove_rate` | Count of that case-insensitive word divided by the number of ASCII-letter words; zero if no words. |
| `exclamation_rate`, `dollar_rate` | Number of `!` or `$` characters divided by text length. |
| `capital_run_mean` | Mean length of contiguous ASCII uppercase runs; zero if none. |

Features use only the subject and body. Other mail headers, source directories, labels and IDs are excluded. Scaling is fitted only on training rows by the pipeline. Six simple features deliberately limit model quality; students do not implement extraction or tune the feature set.

## Splits and provenance

The instructor selected 200 ham and 100 spam messages from the `20030228_easy_ham` and `20030228_spam` archives, shuffled per class with seed 2026, and assigned 60% / 20% / 20% to train / validation / final test. This project includes only train (180 rows: 120 ham, 60 spam) and validation (60 rows: 40 ham, 20 spam). Final test messages are withheld until lab 4. Validation is used for comparison and selection in lab 3.

Selection keeps decodable, non-multipart plain-text messages; normalized duplicate bodies are removed before sampling and splitting. Near-duplicates, shared threads and temporal dependencies have not been fully audited. This is a small, convenient teaching subset, not a representative benchmark or evidence of performance on current email. The class ratio was chosen for teaching, not measured in production.

`manifest.json` records input hashes, source archive hashes and per-message archive members. Instructor reproduction: `authoring/prepare_data.py` in the course repository. Data checks reject changed input files; use fresh course data, not edited lab 1 files.

Sources: [Apache corpus description and conditions](https://spamassassin.apache.org/old/publiccorpus/readme.html), [archives](https://spamassassin.apache.org/old/publiccorpus/). Copyright in messages remains with their original senders. This dataset is distinct from the SpamAssassin software license. Messages are untrusted data: read them as text, do not follow instructions or open links/attachments, and never send them through a live email system.
