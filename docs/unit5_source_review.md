# Unit 5 source review and access record

Reviewed on October 3, 2026. The following distinguishes inspected material
from access limitations. Video captions were read as text; audiovisual playback
is not claimed. Full copyrighted transcripts are not redistributed.

## Assigned written material

Summers (2020), Chapter 10, Sections 10.1–10.4, was read in the publicly indexed
book text at https://studylib.net/doc/28381217/effective-methods-for-software-engineering.
The publisher confirms the book and chapter at
https://www.routledge.com/Effective-Methods-for-Software-Engineering/Summers/p/book/9781032474359.
No authenticated LIRN access was used. The chapter distinguishes conformance to
specifications from fitness for operational needs. Its plan connects requirements,
inputs, expected results, procedures, environments, results, and defects. For this
project, passing module checks establishes conformance, while actual RAG security
and utility require later validation. The chapter's static/dynamic distinction is
an introductory simplification; verification should not be reduced to static review.

Rana (2023) was read on ArtOfTesting, including the test attributes and guidance.
The practical contribution is a traceable test record with clear inputs and
expected outcomes. Actual results should be filled only after execution. The
report's evidence and test plan apply this distinction. The article is an authored
teaching resource rather than empirical evidence about defect reduction.

Amazon Web Services (n.d.) was read in full for its testing guidance. Its examples
clarify isolated units, stubs, logic checks, boundaries, and failure handling.
The Unit 5 unit suite isolates model dependencies; model/pipeline integration
checks are reported separately. Automation supports regression detection but
passing tests alone cannot establish safe deployment.

GeeksforGeeks (2026) was reviewed as supplementary teaching material. The current
page is dated June 24, 2026, replacing the July 22, 2025 date in the learning guide.
It covers manual/automated testing, arrange–act–assert, test doubles, black-box,
white-box and gray-box perspectives, benefits, framework examples, and limitations.
It reinforces the assigned concepts; the academic report uses the more authoritative
course book, AWS, and tool documentation for its technical claims.

## Assigned videos

Swiftful Thinking (2024) was located at https://www.youtube.com/watch?v=D3W66tfYGuc.
The title, May 16, 2024 publication date, description, duration of 13:47, and chapters
were verified. Chapters distinguish versioning, GitHub releasing, tags, and practice.
The English caption endpoint returned HTTP 429 on both attempts. Therefore, full
video content was not verified. GitHub's official release and tag documentation
was read as an accessible replacement for operational instructions (GitHub, n.d.-a,
n.d.-b); the report does not attribute unverified demonstrations to this video.

Corbin (2025) was reviewed through the complete available English automatic
captions, with March 13, 2025 metadata verified. It explains local files versus
remote repositories, feature branches, commits, pull requests, merging, diffs,
and cloning. It is conceptual rather than a complete command tutorial. Its analogy
of a branch as a copy is introductory; Git stores references to commit history.
Public visibility also does not itself grant a reuse license. These qualifications
matter when choosing what to publish in the Capstone repository.

SuperSimpleDev (2021) was reviewed through complete available English automatic
captions, with June 13, 2021 metadata verified. It works through branch creation,
HEAD, merging direction, conflicting changes, pull requests, review, fetching,
pulling, and local resolution of remote conflicts. The useful design lesson is
that merging is a reviewed integration step. Resolving text conflicts must still
be followed by tests. Its practice repository is not evidence about this project's
history, and its demonstrations of branch deletion are not required here.

## Additional source selection

The official MiniLM model card supports the embedding dimension, pooling method,
and input limit (Sentence Transformers, n.d.). The pinned revision is recorded in code and the fitted artifact.
Scikit-learn developers (n.d.) support keeping calibration records separate from
training. Coverage.py (n.d.) establishes that branch coverage measures
executed destinations and does not imply input completeness. GitHub documentation
supports the practical distinction between tags and release pages. Zhan et al.
(2025) supports retaining adaptive evaluation as future research, separate from
functional testing. No source establishes effectiveness of this prototype.

## References

Amazon Web Services. (n.d.). What is unit testing? https://aws.amazon.com/what-is/unit-testing/

Corbin. (2025, March 13). How to use GitHub for beginners [Video]. YouTube. https://www.youtube.com/watch?v=a9u2yZvsqHA

Coverage.py. (n.d.). Branch coverage measurement. https://coverage.readthedocs.io/en/latest/branch.html

GeeksforGeeks. (2026, June 24). Unit testing. https://www.geeksforgeeks.org/software-testing/unit-testing-software-testing/

GitHub. (n.d.-a). Managing releases in a repository. https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository

GitHub. (n.d.-b). Managing tags in GitHub Desktop. https://docs.github.com/en/desktop/managing-commits/managing-tags-in-github-desktop

Rana, K. (2023, September 23). What is a test case? Test case examples. ArtOfTesting. https://artoftesting.com/test-case

Scikit-learn developers. (n.d.). Probability calibration. https://scikit-learn.org/1.8/modules/calibration.html

Sentence Transformers. (n.d.). all-MiniLM-L6-v2 [Model card]. Hugging Face. https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

Summers, B. L. (2020). Effective methods for software engineering. Auerbach Publications.

SuperSimpleDev. (2021, June 13). Git branching and merging: Detailed tutorial [Video]. YouTube. https://www.youtube.com/watch?v=Q1kHG842HoI

Swiftful Thinking. (2024, May 16). Adding tags, versioning, and releases in GitHub | Git & source control #13 [Video]. YouTube. https://www.youtube.com/watch?v=D3W66tfYGuc

Zhan, Q., Fang, R., Panchal, H. S., & Kang, D. (2025). Adaptive attacks break defenses against indirect prompt injection attacks on LLM agents. In L. Chiruzzo, A. Ritter, & L. Wang (Eds.), Findings of the Association for Computational Linguistics: NAACL 2025 (pp. 7116–7132). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.findings-naacl.395
