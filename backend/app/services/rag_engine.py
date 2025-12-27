"""
RAG Engine
Retrieval Augmented Generation engine using ChromaDB for financial knowledge.
"""

import os
from typing import List, Optional, Dict, Any
from loguru import logger

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB not available. RAG features will be limited.")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("Sentence transformers not available. Using fallback embeddings.")

from app.core.config import settings
from app.models.chat import (
    FinancialDocument,
    FinancialDocumentCategory,
    RAGSearchResult
)


class RAGEngine:
    """
    Retrieval Augmented Generation engine for financial knowledge.
    Uses ChromaDB as the vector store and sentence-transformers for embeddings.
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the RAG engine with ChromaDB and embedding model."""
        if self._initialized:
            return
        
        try:
            if CHROMA_AVAILABLE:
                # Initialize ChromaDB
                persist_dir = settings.chroma_persist_directory
                os.makedirs(persist_dir, exist_ok=True)
                
                self.client = chromadb.PersistentClient(
                    path=persist_dir,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                
                # Get or create collection
                self.collection = self.client.get_or_create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"description": "Financial knowledge base for ClariFi AI"}
                )
                
                logger.info(f"ChromaDB initialized with collection: {settings.chroma_collection_name}")
            
            if EMBEDDINGS_AVAILABLE:
                # Initialize embedding model
                self.embedding_model = SentenceTransformer(settings.embedding_model)
                logger.info(f"Embedding model loaded: {settings.embedding_model}")
            
            self._initialized = True
            
            # Seed initial documents if collection is empty
            if self.collection and self.collection.count() == 0:
                await self._seed_initial_documents()
                
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {e}")
            # Continue without RAG features
            self._initialized = True
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if self.embedding_model:
            return self.embedding_model.encode(text).tolist()
        # Fallback: simple hash-based embedding (not recommended for production)
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        # Create a simple 384-dimensional vector from the hash
        hash_bytes = hash_obj.digest()
        return [float(b) / 255.0 for b in hash_bytes * 12][:384]
    
    async def add_document(self, document: FinancialDocument) -> str:
        """
        Add a document to the knowledge base.
        
        Args:
            document: Financial document to add
            
        Returns:
            Document ID
        """
        if not self.collection:
            logger.warning("ChromaDB collection not available")
            return ""
        
        try:
            # Generate document ID
            import uuid
            doc_id = document.id or str(uuid.uuid4())
            
            # Chunk the document for better retrieval
            chunks = self._chunk_document(document.content)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                
                self.collection.add(
                    ids=[chunk_id],
                    documents=[chunk],
                    embeddings=[self._get_embedding(chunk)],
                    metadatas=[{
                        "document_id": doc_id,
                        "title": document.title,
                        "category": document.category.value if hasattr(document.category, 'value') else document.category,
                        "source": document.source,
                        "chunk_index": i,
                        "last_updated": document.last_updated
                    }]
                )
            
            logger.info(f"Added document: {document.title} with {len(chunks)} chunks")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return ""
    
    def _chunk_document(
        self,
        content: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        Split document into chunks for better retrieval.
        Uses semantic chunking based on paragraphs and sentences.
        """
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If no chunks were created (single paragraph), split by sentences
        if len(chunks) == 1 and len(chunks[0]) > chunk_size:
            sentences = chunks[0].replace('. ', '.\n').split('\n')
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content]
    
    async def search(
        self,
        query: str,
        category: Optional[FinancialDocumentCategory] = None,
        n_results: int = 5,
        min_relevance: float = 0.3
    ) -> List[RAGSearchResult]:
        """
        Search for relevant documents based on query.
        
        Args:
            query: Search query
            category: Optional category filter
            n_results: Maximum number of results
            min_relevance: Minimum relevance score (0-1)
            
        Returns:
            List of relevant document chunks with scores
        """
        if not self.collection or self.collection.count() == 0:
            # Return empty results if no documents
            return []
        
        try:
            # Build query filter
            where_filter = None
            if category:
                where_filter = {
                    "category": category.value if hasattr(category, 'value') else category
                }
            
            # Search
            query_embedding = self._get_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            search_results = []
            
            if results and results.get("documents") and len(results["documents"]) > 0:
                documents = results["documents"][0]
                metadatas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
                
                for i, doc in enumerate(documents):
                    # Convert distance to similarity score (assuming L2 distance)
                    # Lower distance = higher similarity
                    distance = distances[i] if i < len(distances) else 1.0
                    relevance = max(0, 1 - (distance / 2))  # Normalize to 0-1
                    
                    if relevance >= min_relevance:
                        metadata = metadatas[i] if i < len(metadatas) else {}
                        
                        search_results.append(RAGSearchResult(
                            content=doc,
                            category=metadata.get("category", "general"),
                            source=metadata.get("source", "unknown"),
                            relevance_score=round(relevance, 3)
                        ))
            
            # Sort by relevance
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            logger.debug(f"RAG search for '{query[:50]}...' returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return []
    
    async def get_context_for_query(
        self,
        query: str,
        categories: Optional[List[FinancialDocumentCategory]] = None,
        max_context_length: int = 3000
    ) -> str:
        """
        Get combined context from relevant documents for LLM prompting.
        
        Args:
            query: User query
            categories: Optional category filters
            max_context_length: Maximum total context length
            
        Returns:
            Combined context string
        """
        all_results = []
        
        # Search across categories if specified, otherwise search all
        if categories:
            for category in categories:
                results = await self.search(query, category=category, n_results=3)
                all_results.extend(results)
        else:
            all_results = await self.search(query, n_results=5)
        
        # Sort by relevance and combine
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        context_parts = []
        current_length = 0
        
        for result in all_results:
            if current_length + len(result.content) > max_context_length:
                break
            
            context_parts.append(
                f"[Source: {result.source} | Category: {result.category}]\n{result.content}"
            )
            current_length += len(result.content)
        
        return "\n\n---\n\n".join(context_parts)
    
    async def _seed_initial_documents(self) -> None:
        """Seed the knowledge base with initial financial documents."""
        initial_documents = [
            FinancialDocument(
                title="Emergency Fund Basics",
                content="""An emergency fund is a savings buffer that helps you cover unexpected expenses or financial emergencies without going into debt. 

Key Guidelines:
- Aim for 3-6 months of living expenses
- For single-income households, consider 6-12 months
- Keep it in a liquid, easily accessible account like a savings account
- Don't invest emergency funds in volatile assets
- Replenish the fund after using it

When to use your emergency fund:
- Job loss or income reduction
- Medical emergencies not covered by insurance
- Major car or home repairs
- Unexpected family emergencies

Building your emergency fund:
1. Calculate your monthly essential expenses
2. Set a target amount (3-6 months of expenses)
3. Automate regular contributions
4. Consider a high-yield savings account for better returns
5. Resist the temptation to use it for non-emergencies""",
                category=FinancialDocumentCategory.SAVINGS,
                source="Financial Planning Guidelines",
                last_updated="2024-01-01"
            ),
            FinancialDocument(
                title="50/30/20 Budget Rule",
                content="""The 50/30/20 rule is a simple budgeting framework that divides your after-tax income into three categories:

50% for Needs (Essential Expenses):
- Housing (rent/mortgage)
- Utilities (electricity, water, internet)
- Groceries
- Transportation
- Insurance premiums
- Minimum debt payments
- Healthcare

30% for Wants (Discretionary Spending):
- Dining out and entertainment
- Shopping and hobbies
- Subscriptions and memberships
- Travel and vacations
- Personal care and lifestyle upgrades

20% for Savings and Debt Repayment:
- Emergency fund
- Retirement contributions
- Investment accounts
- Extra debt payments above minimums
- Financial goals (house down payment, education)

Tips for implementing the 50/30/20 rule:
1. Track your spending for a month to understand current habits
2. Categorize each expense into needs, wants, or savings
3. Adjust spending if any category exceeds its allocation
4. Automate savings to ensure consistency
5. Review and adjust quarterly based on income changes""",
                category=FinancialDocumentCategory.BUDGETING,
                source="Personal Finance Best Practices",
                last_updated="2024-01-01"
            ),
            FinancialDocument(
                title="Investment Diversification Principles",
                content="""Diversification is a risk management strategy that spreads investments across various financial instruments, industries, and categories.

Key Principles:

1. Asset Class Diversification:
- Equity (stocks, mutual funds)
- Fixed income (bonds, FDs)
- Real assets (real estate, gold)
- Cash equivalents

2. Geographic Diversification:
- Domestic investments
- International exposure
- Emerging markets allocation

3. Sector Diversification:
- Technology
- Healthcare
- Financial services
- Consumer goods
- Energy and utilities

4. Time Diversification (Rupee Cost Averaging):
- Invest regularly regardless of market conditions
- SIP (Systematic Investment Plan) is effective
- Reduces impact of market volatility

Risk-Return Relationship:
- Higher potential returns generally mean higher risk
- Conservative: 30% equity, 60% debt, 10% gold
- Moderate: 50% equity, 40% debt, 10% gold
- Aggressive: 70% equity, 20% debt, 10% gold

Important Considerations:
- Rebalance portfolio annually
- Adjust allocation based on age and goals
- Don't put all eggs in one basket
- Review investments quarterly""",
                category=FinancialDocumentCategory.INVESTMENT,
                source="Investment Strategy Guidelines",
                last_updated="2024-01-01"
            ),
            FinancialDocument(
                title="Tax Saving Instruments in India",
                content="""Tax saving options under Section 80C (up to ₹1.5 lakh deduction):

1. Equity Linked Savings Scheme (ELSS):
- Lock-in: 3 years (shortest among 80C options)
- Returns: Market-linked, historically 12-15% CAGR
- Risk: High (equity exposure)

2. Public Provident Fund (PPF):
- Lock-in: 15 years (partial withdrawal after 7 years)
- Returns: Government-set, currently ~7.1%
- Risk: Low (government-backed)

3. National Pension System (NPS):
- Additional ₹50,000 deduction under 80CCD(1B)
- Lock-in: Until retirement (60 years)
- Returns: 9-12% historically
- Risk: Low to moderate

4. Tax-Saving Fixed Deposits:
- Lock-in: 5 years
- Returns: 6-7% (bank dependent)
- Risk: Low

5. Life Insurance Premiums:
- Term insurance is cost-effective
- Premium up to ₹1.5 lakh qualifies

6. Employee Provident Fund (EPF):
- Mandatory for salaried employees
- Returns: ~8.1%

Other Deductions:
- Section 80D: Health insurance premiums (up to ₹25,000/₹50,000)
- Section 80E: Education loan interest (no upper limit)
- Section 24: Home loan interest (up to ₹2 lakh)

Tax Planning Tips:
- Start investing early in the financial year
- Don't invest just for tax savings; consider returns
- Match investments with financial goals
- Consider lock-in periods before investing""",
                category=FinancialDocumentCategory.TAX,
                source="Indian Tax Planning Guide 2024",
                last_updated="2024-01-01"
            ),
            FinancialDocument(
                title="Health Insurance Fundamentals",
                content="""Health insurance is essential protection against medical expenses. Here's what you need to know:

Types of Health Insurance:
1. Individual Health Plans: Cover single person
2. Family Floater Plans: Cover entire family under one sum insured
3. Critical Illness Plans: Lump sum on diagnosis of specified illnesses
4. Top-up Plans: Additional coverage above base policy

Key Terms:
- Sum Insured: Maximum amount the insurer will pay
- Premium: Annual/monthly payment for coverage
- Waiting Period: Time before certain conditions are covered
- Pre-existing Diseases: Conditions you have before buying policy
- Co-payment: Percentage you pay from claim amount
- No Claim Bonus: Discount for claim-free years

How Much Coverage Do You Need:
- Minimum: 5-10 lakhs for individuals
- Recommended: 10-20 lakhs for families
- Consider city of residence (metro cities need higher coverage)
- Add top-up plans for cost-effective higher coverage

Claim Process:
1. Cashless: Treatment at network hospitals, insurer pays directly
2. Reimbursement: Pay first, claim later from insurer

Important Considerations:
- Buy early to minimize waiting periods
- Disclose all pre-existing conditions honestly
- Check network hospital list in your area
- Understand exclusions before buying
- Port policy if unsatisfied (without losing benefits)""",
                category=FinancialDocumentCategory.INSURANCE,
                source="Insurance Planning Guidelines",
                last_updated="2024-01-01"
            ),
            FinancialDocument(
                title="Debt Management Strategies",
                content="""Effective debt management is crucial for financial health. Here are proven strategies:

Types of Debt:
1. Good Debt: Creates value (education loans, home loans)
2. Bad Debt: Depreciating assets or consumption (credit card, personal loans)

Debt Repayment Strategies:

Avalanche Method:
- Pay minimum on all debts
- Put extra money toward highest-interest debt first
- Mathematically optimal, saves most interest

Snowball Method:
- Pay minimum on all debts
- Put extra money toward smallest balance first
- Psychologically motivating (quick wins)

Debt Consolidation:
- Combine multiple debts into one loan
- Usually at lower interest rate
- Simplifies payments

Key Ratios to Monitor:
- Debt-to-Income Ratio: Should be below 40%
- EMI-to-Income Ratio: Should be below 50%
- Credit Utilization: Keep below 30% of credit limit

Action Steps for Debt-Free Living:
1. List all debts with interest rates and balances
2. Create a realistic repayment budget
3. Stop taking new debt while repaying
4. Build a small emergency fund to prevent new debt
5. Consider balance transfer for high-interest cards
6. Negotiate with lenders for better rates
7. Celebrate milestones to stay motivated""",
                category=FinancialDocumentCategory.LOAN,
                source="Debt Management Best Practices",
                last_updated="2024-01-01"
            ),
            FinancialDocument(
                title="Retirement Planning Basics",
                content="""Planning for retirement requires understanding how much you'll need and how to save for it.

Estimating Retirement Corpus:
1. Calculate annual expenses in retirement (typically 70-80% of current)
2. Factor in inflation (assume 6-7% annually)
3. Consider retirement duration (plan for 25-30 years)
4. Rule of thumb: Need 25-30x annual expenses as corpus

Retirement Investment Options:

1. National Pension System (NPS):
- Tax benefits under 80CCD
- Professional fund management
- Annuity requirement at maturity

2. Employee Provident Fund (EPF):
- Employer contribution matching
- Tax-free interest
- Good for long-term accumulation

3. Public Provident Fund (PPF):
- Safe, government-backed
- Tax-free returns
- 15-year lock-in

4. Mutual Funds:
- Higher return potential
- SIP for disciplined investing
- Consider balanced/hybrid funds as you age

Age-Based Asset Allocation:
- 20s-30s: 80% equity, 20% debt
- 40s: 60% equity, 40% debt
- 50s: 40% equity, 60% debt
- 60+: 20-30% equity, 70-80% debt

Key Retirement Planning Tips:
- Start as early as possible (power of compounding)
- Increase savings with every salary hike
- Don't withdraw retirement funds prematurely
- Account for healthcare costs in retirement
- Consider inflation-indexed investments
- Have multiple income streams in retirement""",
                category=FinancialDocumentCategory.RETIREMENT,
                source="Retirement Planning Guidelines",
                last_updated="2024-01-01"
            ),
            FinancialDocument(
                title="Mutual Fund Investment Guide",
                content="""Mutual funds pool money from investors to invest in diversified portfolios managed by professionals.

Types of Mutual Funds:

By Asset Class:
1. Equity Funds: Invest in stocks (high risk, high return)
2. Debt Funds: Invest in bonds/fixed income (low risk)
3. Hybrid Funds: Mix of equity and debt
4. Money Market Funds: Short-term instruments

By Investment Style:
1. Large Cap: Top 100 companies, lower risk
2. Mid Cap: 101-250 companies, moderate risk
3. Small Cap: Beyond 250, higher risk
4. Multi Cap: Across market caps
5. Index Funds: Track market indices, low cost
6. Sectoral Funds: Specific sectors like IT, Pharma

Investment Methods:
1. SIP (Systematic Investment Plan):
- Invest fixed amount monthly
- Rupee cost averaging
- Disciplined approach
- Start with as little as ₹500/month

2. Lump Sum:
- One-time investment
- Better when markets are low
- Requires timing knowledge

Key Metrics to Evaluate:
- CAGR: Compound Annual Growth Rate
- Expense Ratio: Lower is better (<1% for passive, <2% for active)
- Alpha: Excess returns over benchmark
- Sharpe Ratio: Risk-adjusted returns
- AUM: Assets Under Management

Exit Load and Taxation:
- Exit load: Fee for early redemption (usually 1% if <1 year)
- LTCG on equity: 10% on gains above ₹1 lakh (holding >1 year)
- STCG on equity: 15% (holding <1 year)
- Debt funds: As per income tax slab

Investment Tips:
- Start with large-cap or index funds
- Diversify across fund houses
- Review performance annually
- Don't switch funds frequently
- Stay invested for long term (5+ years)""",
                category=FinancialDocumentCategory.INVESTMENT,
                source="Mutual Fund Investment Guide",
                last_updated="2024-01-01"
            )
        ]
        
        for doc in initial_documents:
            await self.add_document(doc)
        
        logger.info(f"Seeded {len(initial_documents)} initial documents to knowledge base")


# Global RAG engine instance
rag_engine = RAGEngine()
