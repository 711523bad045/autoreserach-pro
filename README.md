-> AutoResearch Pro — Autonomous Research Assistant

  *AutoResearch Pro is an AI-powered autonomous research assistant that automatically:
  *Searches trusted sources on the web (Wikipedia)
  *Scrapes and cleans the content
  *Splits the data into intelligent chunks
  *Uses an LLM (Ollama Qwen2.5) to generate a full structured research report
  *Stores everything in a database
  *Allows asking questions from the generated research
  *Can convert the report into IEEE research paper format
<img width="1919" height="963" alt="Screenshot 2026-01-27 141953" src="https://github.com/user-attachments/assets/42c89454-27c6-42e7-9b2d-b0c15428f2cf" />
<img width="1890" height="979" alt="Screenshot 2026-01-27 141938" src="https://github.com/user-attachments/assets/aa439307-9396-4184-8929-b77b165ef454" />
<img width="1919" height="965" alt="Screenshot 2026-01-27 141902" src="https://github.com/user-attachments/assets/4adeda8f-c479-4727-bfe3-a0fea67ad417" />
<img width="1907" height="902" alt="Screenshot 2026-01-27 141850" src="https://github.com/user-attachments/assets/400ab794-38d1-46a6-82bd-381fb4a66736" />
<img width="1914" height="970" alt="Screenshot 2026-01-27 141820" src="https://github.com/user-attachments/assets/e10fc56c-d5aa-4095-8fc7-276f65d6674c" />
<img width="1919" height="916" alt="Screenshot 2026-01-27 141803" src="https://github.com/user-attachments/assets/d6934ced-07c0-40c1-b86d-0712df03c255" />



This system automates the entire research workflow from topic → sources → content → report.

-> Why This Project?

- Traditional research takes:
 *Hours of searching
 *Reading multiple websites
 *Copying content
 *Structuring the document
 *Writing the report manually
AutoResearch Pro does all of this automatically.
Just enter a topic → the system generates a complete research report.

-> System Architecture (High Level)
User → Frontend → FastAPI Backend → Web Search → Web Scraping → Chunking → LLM → Database → UI

- Complete Workflow (Step by Step)
 Step 1: Topic Input
         *User enters a research topic in the UI, for example:
         *"Artificial Intelligence in Healthcare"

 Step 2: Web Search (Wikipedia)
 
  The system searches Wikipedia for:
        *Trusted
        *Clean
        *High-quality sources
        *Multiple relevant URLs are collected.
  Why Wikipedia?
        *Structured
        *Reliable
        *Clean HTML
  Perfect for research base content

 Step 3: Web Scraping (BeautifulSoup4)
   Each URL is downloaded using BeautifulSoup4
   The system extracts:
  Main content
     *Removes menus, ads, useless text
     *The clean text is stored in the database as Sources

 Step 4: Chunking & Preprocessing
     *Large text is split into smaller chunks (~300–350 words each).
 Why chunking?
     *Small LLM model (0.5B) has context limits
 Chunking:
    *Preserves quality
    *Improves accuracy
    *Avoids hallucination
    *Makes generation more stable
    *These chunks are saved in the database.

 Step 5: RAG (Retrieval Augmented Generation)
    *This project uses RAG architecture:
    *The LLM does NOT answer from memory alone.

  Instead:
     *Relevant chunks are selected
     *Injected into the prompt
     *LLM generates content using real scraped data
  This:
    *Increases factual accuracy
    *Reduces hallucination
    *Makes output grounded in real sources

 Step 6: Report Generation (Ollama Qwen2.5:0.5B)
    The system uses:
      *qwen2.5:0.5b
    Why this model?
      *Very fast
      *Runs locally (no API cost)
      *Good enough for structured generation

- Low RAM usage

    Tradeoff:
      *Slightly lower language quality
      *But we compensate using:
      *Chunking
      *Strong prompts
      *RAG

 Step 7: Section-by-Section Writing
      *The report is generated in parts:
      *Introduction
      *Background
      *Core Concepts
      *Architecture
      *Applications
      *Advantages & Limitations
      *Conclusion

Each section:
    *Uses chunk context
    *Is appended to the final report
    *Is saved to the database

 Step 8: Source Storage

  All scraped sources are:
    *Stored in DB
    *Displayed in UI
    *Added to the report as references

 Step 9: Ask Questions From Report

  There is a Q&A Bot:
    *Uses the same qwen2.5:0.5b model
    *Answers only from the generated report
    *Uses report content as context
    *Fast and local

 Step 10: Convert to IEEE Format

  The system can convert the report into:
     *Proper IEEE research paper format
    Using:
    *qwen2.5:1.5b (higher quality model)
    This:
     *Removes unwanted text
     *Makes language formal
    Structures paper into:
     *Abstrac
     *Keywords
     *Introduction
     *Sections
     *Conclusion
     *References

-> Tech Stack
   Backend
    *Python
    *FastAPI
    *SQLAlchemy
    *MySQL
    *BeautifulSoup4
    *Ollama

   AI Models
    *qwen2.5:0.5b → Fast generation   
    *qwen2.5:1.5b → High quality IEEE conversion

   Frontend
    *React
    *Axios

   Database Tables
     *research_projects → Topics
     *reports → Generated reports
     *sources → Scraped websites
     *chunks → Chunked content
     *report_sections → Split sections
     *ieee_reports → IEEE formatted papers
<img width="1862" height="957" alt="Screenshot 2026-01-27 104101" src="https://github.com/user-attachments/assets/9cec0d5e-8934-4151-bdbd-87ca175313c0" />

   Key Features
    * Fully automatic research
    * Uses real web data
    * RAG-based generation
    * Local LLM (No API cost)
    * Fast generation
    * IEEE conversion
    * Q&A chatbot
    * Source tracking
    * Database persistence




