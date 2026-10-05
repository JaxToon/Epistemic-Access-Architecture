# RESEARCH CONTEXT HANDOFF
## Epistemic Access Architecture (EAA) for Reducing Hallucination in Large Language Models

> Purpose: this file is a persistent context handoff for future chats.  
> If this conversation is a temporary chat, upload/read this file at the beginning of a new chat so the assistant can reconstruct the research direction without relying on prior chat memory.

---

# 1. PROJECT IDENTITY

Working research program:

**Epistemic Access Architecture (EAA)**

Core research theme:

**Knowledge accessibility, epistemic control, and hallucination in Large Language Models (LLMs).**

Central intuition:

> A model can possess, encode, or have access to relevant knowledge without necessarily being able to reliably access, integrate, and use that knowledge at the moment of generation.

Therefore:

**Knowledge Presence != Knowledge Accessibility != Knowledge Utilization**

The research is inspired by neuroscience, especially split-brain research, but the thesis must NOT depend on claiming that an LLM literally works like a biological human brain.

The neuroscience analogy should be treated as a **functional inspiration**:

- specialized processing systems;
- limited/intermittent communication;
- information integration;
- conflict monitoring;
- arbitration;
- coherent final behavior.

The scientific claim should be about **information accessibility and causal control of generation**, not about anatomical replication of the human brain.

---

# 2. ORIGINAL IDEA FROM THE USER

Initial intuition:

The user remembered classical split-brain experiments associated with Roger Sperry, Michael Gazzaniga, Joseph Bogen, and others.

In simplified terms, information could be delivered to one visual field/hemisphere while communication between hemispheres was severely restricted. The language-capable system could then produce a plausible explanation despite not having access to all of the information that influenced behavior.

The important phenomenon is:

> The system may have incomplete access to the evidence, yet still be pressured to produce a coherent explanation.

This was connected to LLM hallucination.

Initial hypothesis was roughly:

> LLMs hallucinate because they do not “see” all of the knowledge contained in their training.

This was refined because an LLM does not retain the training corpus as a directly browsable database inside the model. Pretraining transforms information through optimization into distributed/parametric representations, and the relation between “learned” and “retrievable/usable” is non-trivial.

Better formulation:

> Hallucination may partly arise from a gap between knowledge that exists or is available to the system and knowledge that is accessible, integrated, and grounded at generation time.

---

# 3. CORE HYPOTHESES

## H1 — Knowledge Accessibility Hypothesis

> Hallucination is partly determined by the accessibility of relevant knowledge at generation time, rather than only by whether the knowledge exists somewhere in the model/system.

Conceptual relationship:

P(Hallucination | x) should increase as relevant knowledge accessibility decreases, controlling for knowledge availability.

Notational starting point:

- K = total learned/available knowledge
- A(K,x) = accessibility of relevant knowledge for query x
- E(x) = evidence available to the generation process
- H = unsupported/hallucinated claim

Conceptual hypothesis:

    Knowledge Exists
           !=
    Knowledge Accessible
           !=
    Knowledge Used Correctly

---

## H2 — Epistemic Integration Hypothesis

> A language architecture that functionally separates evidence/knowledge processing from linguistic generation, while preserving controlled communication between the two, can reduce unsupported generation relative to a monolithic generator under matched knowledge conditions.

The idea is not simply:

“add a verifier after the model.”

The stronger idea is:

> Make epistemic processing a first-class computational subsystem that has structured communication with generation and can influence/intervene in the generation process.

---

# 4. EPISTEMIC STATES

A central concept for the research is to distinguish at least four knowledge states.

## State A — Unknown

The relevant fact was never present in the controlled knowledge source/training corpus.

Expected behavior:
- the system should ideally recognize lack of knowledge;
- abstention may be appropriate.

## State B — Known but Inaccessible

The fact was present in the model’s known/training environment or otherwise legitimately available to the overall system, but the generator cannot reliably access or retrieve it.

This is the most important state for the hypothesis.

## State C — Known and Accessible

The relevant fact exists and the system can retrieve/integrate it appropriately.

## State D — Conflicted

Relevant evidence exists but sources/representations conflict.

The system must identify the conflict rather than arbitrarily generate a plausible answer.

These states create a better taxonomy than simply:

    “the model knows”
    vs
    “the model does not know”

---

# 5. IMPORTANT PRIOR ART / LITERATURE LANDSCAPE

The idea is NOT completely unprecedented. The research must position itself against several strands of prior work.

## 5.1 Split-brain / confabulation

Classical split-brain work by Sperry/Gazzaniga/Bogen demonstrated effects of restricted inter-hemispheric information integration.

Important caution:

Do not claim:
- “left brain = language”
- “right brain = hallucination”
- “LLM = two human hemispheres”

Use the research only as a functional analogy for:
- partial information access;
- communication bottlenecks;
- post-hoc/confabulatory explanation;
- distributed specialized processing.

Modern neuroscience reviews also caution against simplistic “two separate minds” interpretations.

---

## 5.2 Lost in the Middle

TACL / 2024 line of work:

**“Lost in the Middle: How Language Models Use Long Contexts”**

Important implication:

> Information being present in the context does not guarantee that the LLM will effectively use it.

The phenomenon provides supporting evidence for:

    Presence != Effective Accessibility

This is highly relevant to the research.

---

## 5.3 Knowledge Neurons

EMNLP 2024 work:

**“Knowledge Neurons in Pretrained Transformers” / later work on knowledge recall and factual associations**

Important implication:

Specific factual associations can be investigated/manipulated internally; changing the ability to recall/use such knowledge can change task performance.

Research relevance:

    Knowledge representation/availability
        !=
    Reliable factual recall/use

---

## 5.4 Knowledge Boundary / Internal-State Research

Recent work studies whether model internal states can indicate whether a model “knows” an answer before generation and how confidence/uncertainty can be estimated.

This supports the idea that epistemic state information may exist inside or around the generative model but is not necessarily given explicit architectural authority over generation.

---

## 5.5 Retrieval of Pretraining Data / RETAIN-like work

A particularly relevant 2026 line of work:

**“Parametric Knowledge is Not All You Need: Toward Honest Large Language Models via Retrieval of Pretraining Data”**

Important reason this is valuable:

The Pythia ecosystem provides:
- public model checkpoints;
- known training setup;
- training-data accessibility/auditability.

This creates an experimental environment in which researchers can distinguish:
- never learned;
- learned/available;
- accessible after retrieval;
- inaccessible despite having appeared in training.

This is an attractive foundation for the pilot experiment.

---

## 5.6 RAG / REALM / RETRO

Retrieval-based architectures already separate some knowledge processing from generation.

Relevant examples:
- REALM
- RETRO
- retrieval-augmented generation broadly.

Therefore:

**“reader + generator” alone is NOT novel enough.**

The research novelty must be about:
- epistemic state;
- controlled information flow;
- arbitration;
- causal access intervention;
- explicit distinction between knowledge presence and knowledge accessibility;
- generation constrained/authorized by epistemic evidence.

---

## 5.7 Self-RAG

Self-RAG introduces adaptive retrieval and reflection mechanisms.

Important implication:

The field already has systems where retrieval/reflection can influence generation.

Therefore:

**“RAG with self-reflection” is not sufficient novelty.**

The proposed contribution needs a more explicit causal/architectural theory around epistemic accessibility.

---

## 5.8 Chain-of-Verification (CoVe)

CoVe:
- generate draft;
- create verification questions;
- independently verify;
- generate final response.

Important limitation for our framing:

It is mainly a verification workflow.

The desired EAA architecture should make epistemic processing more fundamental and integrated into the generation control loop.

---

## 5.9 LLM2 / System-2-like verification

Recent work such as LLM2 explores generator + process-verifier / System-2 style reasoning.

Again:

“generator + verifier” is already an active research direction.

The proposed distinction is:

> the epistemic component should control what can legitimately enter generation, rather than merely criticize the output afterward.

---

## 5.10 Neural Arbitration Framework (NAF), 2026

Very important closest prior art.

A 2026 working paper called:

**“Neural Arbitration Framework: A Conceptual Architecture and Research Agenda for Epistemic Arbitration in Large Language Models”**

is highly relevant because it explicitly connects:
- split-brain ideas;
- confabulation;
- generative vs epistemic modes;
- arbitration;
- uncertainty;
- abstention.

Therefore the research must NOT claim:

> “First paper to connect split-brain and LLM hallucination.”

That claim is unsafe.

Instead, the research should attempt to move from conceptual analogy/framework to:

1. operationalized measurement;
2. controlled causal intervention;
3. explicit knowledge-access experiments;
4. experimentally validated architecture.

NAF should be treated as **closest conceptual prior art to beat/extend**, not ignored.

---

# 6. THE PROPOSED RESEARCH GAP

The central proposed research gap:

> Existing work separately studies hallucination, retrieval, verification, uncertainty, knowledge recall, and split-brain-inspired epistemic/generative architectures. What is still insufficiently established is whether a controllable bottleneck in evidence access between a knowledge/epistemic process and the generative process can causally induce hallucination, and whether restoring that access reliably reduces hallucination under matched conditions.

The key research question:

> **Can hallucination be causally induced and mitigated by manipulating the accessibility and communication of relevant evidence between knowledge processing and language generation?**

This is the scientific center of the research.

---

# 7. MAIN RESEARCH QUESTION

## Primary RQ

> Does limiting access to relevant knowledge/evidence between an epistemic processing subsystem and a generative subsystem causally increase hallucination, and does restoring that access causally reduce hallucination?

## Secondary RQs

1. How can “known”, “known-but-inaccessible”, “accessible”, and “conflicted” states be operationalized?
2. Can knowledge accessibility be measured independently of generation accuracy?
3. Does hallucination correlate with an explicit evidence-access bottleneck after controlling for model capability and knowledge budget?
4. What communication channel is sufficient to transfer epistemic state to generation?
5. Is a dedicated epistemic processor better than ordinary RAG or post-hoc verification?
6. Does explicit epistemic arbitration improve calibration and abstention, not only accuracy?
7. Does the effect generalize across model sizes, model families, tasks, and domains?

---

# 8. PROPOSED ARCHITECTURE

Working name:

# Epistemic Access Architecture (EAA)

Functional principle:

> One coherent AI system, multiple specialized cognitive functions.

Not:
- two independent AIs;
- literal human-brain replication;
- left-brain/right-brain copying.

Instead:

    ONE SYSTEM
      |
      +-- Knowledge / Reader System
      |
      +-- Epistemic Memory
      |
      +-- Shared Cognitive Workspace
      |
      +-- Arbitration Controller
      |
      +-- Generative Core
      |
      +-- Final Claim Check

Conceptual architecture:

                  WORLD / KNOWLEDGE
                          |
                          v
                +--------------------+
                |   KNOWLEDGE READER |
                |                    |
                | retrieve           |
                | interpret          |
                | extract evidence   |
                | reconcile          |
                | verify             |
                +---------+----------+
                          |
                          v
                +--------------------+
                |  EPISTEMIC MEMORY  |
                |                    |
                | claims             |
                | sources            |
                | confidence         |
                | contradictions     |
                | temporal validity  |
                +---------+----------+
                          |
                          v
                +--------------------+
                | SHARED WORKSPACE   |
                +---------+----------+
                          |
                          v
                +--------------------+
                |    ARBITRATION     |
                |                    |
                | answer?            |
                | enough evidence?   |
                | conflict?          |
                | retrieve more?     |
                | abstain?           |
                +----+-----------+---+
                     |           |
                   PASS       RETRIEVE/REPAIR
                     |           |
                     v           |
                +--------------------+
                |    GENERATOR       |
                |                    |
                | reasoning          |
                | composition        |
                | natural language   |
                +---------+----------+
                          |
                          v
                +--------------------+
                | FINAL CLAIM CHECK  |
                +---------+----------+
                          |
                          v
                       OUTPUT

Key conceptual separation:

Reader/Epistemic subsystem:
> “What do we have evidence to say?”

Generator:
> “How should we express it?”

Arbitrator:
> “Is the generator epistemically authorized to say it?”

---

# 9. THE “CORPUS CALLOSUM” ANALOGY

A useful abstraction:

    Knowledge subsystem
            |
            | evidence / state
            v
    Communication channel
            |
            v
    Generative subsystem

The communication channel is the functional analogue of an integration pathway.

The research should experimentally manipulate it:
- full access;
- partial access;
- restricted access;
- restored access.

Important:

Do not overclaim biological equivalence.

The useful concept is:

**controlled information integration**, not biological anatomy.

---

# 10. THE FIRST PILOT STUDY

## Pilot objective

Do NOT start by building the final architecture.

First test:

> **Does known-but-inaccessible knowledge produce a measurable increase in hallucination?**

Recommended starting platform:

**Pythia** or another model ecosystem with auditable/public training information.

Why Pythia?

- public model checkpoints;
- public training setup;
- training progression;
- useful for studying whether/when information was learned;
- suitable for controlled causal experiments.

---

# 11. PILOT EXPERIMENTAL CONDITIONS

Minimum condition set:

### Condition A — Never Learned / Unknown

The fact was not present in the controlled knowledge source.

Expected:
- model may not know;
- good behavior may be abstention.

### Condition B — Learned + Accessible

The fact is available and correctly retrievable.

Expected:
- high factual accuracy;
- low hallucination.

### Condition C — Learned + Access Restricted

The fact exists in the model/knowledge environment but the relevant access pathway is blocked or degraded.

Expected under H1:
- accuracy decreases;
- unsupported/confident claims increase.

### Condition D — Access Restored

Restore the communication/access pathway.

Expected:
- performance and truthfulness improve again.

The most powerful causal sequence is:

    FULL ACCESS
        ↓
    low hallucination

    ACCESS BLOCKED
        ↓
    hallucination increases

    ACCESS RESTORED
        ↓
    hallucination decreases

---

# 12. “SPLIT-BRAIN AI” EXPERIMENT

A later experiment can explicitly create:

    Knowledge Reader
          |
          X   <- intervention
          |
       Generator

Compare communication bandwidth:

    100%
    75%
    50%
    25%
    10%
    0%

Measure:

- hallucination rate;
- factual accuracy;
- evidence attribution;
- calibration;
- confidence;
- abstention;
- unsupported-claim rate.

Core test:

    Access ↓  -> Hallucination ↑

Then perform restoration:

    Access restored -> Hallucination ↓

This provides a causal interpretation if properly controlled.

---

# 13. CONTROLLED “ACCESS” DEFINITIONS

Access must be operationalized carefully.

Possible forms:

### A. Retrieval access
Reader is allowed to retrieve relevant document chunks.

### B. Representation access
Reader can encode evidence, but generator only receives restricted/structured summaries.

### C. Bandwidth restriction
Limit number of claims/tokens/embeddings passed through the communication interface.

### D. Semantic masking
Block specific evidence dimensions while preserving unrelated information.

### E. Timing restriction
Provide evidence only before/after certain generation stages.

### F. Arbitration restriction
Allow evidence into the system but prevent epistemic state from influencing generation.

The last condition is especially useful for distinguishing:
- evidence exists;
- evidence is read;
- evidence actually controls generation.

---

# 14. IMPORTANT DISTINCTION

Avoid the overly broad statement:

> “Show the model the entire training dataset.”

The proposed idea should instead be:

> **Make the entire relevant knowledge environment available to a specialized knowledge/epistemic subsystem, and let that subsystem selectively transfer validated evidence to generation.**

This is more realistic and more biologically/functionally plausible.

Desired flow:

    CORPUS
      ↓
    READER
      ↓
    EPISTEMIC STATE
      ↓
    RETRIEVAL / INTEGRATION
      ↓
    ARBITRATION
      ↓
    GENERATOR

Not:

    CORPUS
      ↓
    dump everything into generator

---

# 15. POTENTIAL NOVELTY CLAIM

A cautious version:

> This research proposes and empirically tests a causal account of hallucination centered on epistemic accessibility: relevant knowledge may exist within the overall knowledge environment while remaining inaccessible or insufficiently integrated into the generative process. The work operationalizes this distinction, manipulates information access and communication as causal variables, and develops an integrated epistemic–generative architecture whose arbitration mechanism controls evidence-grounded generation.

Potential stronger contribution:

> A unified cognitive architecture in which a dedicated epistemic subsystem constructs an explicit epistemic state and a generative subsystem produces language under controlled epistemic arbitration.

Do NOT claim novelty yet until a systematic literature review confirms it.

---

# 16. EXPERIMENTAL BASELINES

At minimum compare:

1. Vanilla causal language model.
2. Vanilla + standard RAG.
3. Self-RAG or equivalent adaptive retrieval.
4. Generator + verifier baseline.
5. Proposed EAA.

For fair comparison:
- matched or carefully controlled model size;
- matched knowledge budget;
- same question sets;
- same source evidence;
- same evaluation criteria.

The key question is not simply:

> “Which model scores highest?”

It is:

> “Does explicit epistemic access control explain and reduce hallucination beyond what ordinary retrieval/verification already achieves?”

---

# 17. METRICS

Primary:
- hallucination rate;
- unsupported claim rate;
- factual accuracy;
- citation/evidence faithfulness.

Secondary:
- calibration;
- expected calibration error;
- abstention precision/recall;
- false refusal;
- evidence utilization;
- evidence-to-claim attribution;
- contradiction detection;
- robustness under distractors;
- robustness under long context;
- latency/compute overhead.

Proposed additional metric:

## Access Sensitivity

Measure change in performance when access is experimentally manipulated.

Conceptually:

    Access Sensitivity
      =
    Δ Hallucination / Δ Access

This should be formalized later.

---

# 18. FALSIFICATION CRITERIA

This is essential for PhD rigor.

The theory should be weakened or rejected if:

1. Hallucination does not increase when relevant knowledge access is blocked.
2. Restoring access does not reliably reduce hallucination.
3. The observed effect disappears after controlling for simple context length/token effects.
4. “Known-but-inaccessible” cannot be distinguished from genuinely unknown cases.
5. Standard RAG alone completely explains the effect.
6. The architecture improves results only because it receives more information or more compute, not because of epistemic separation/arbitration.

The aim is to make the theory capable of being wrong.

---

# 19. MECHANISTIC QUESTIONS AFTER THE PILOT

If the first pilot succeeds, investigate:

### Where is the access failure?

Possibilities:
- retrieval;
- encoding;
- attention allocation;
- representation bottleneck;
- working-memory capacity;
- conflict resolution;
- uncertainty estimation;
- decoding/generation pressure.

Then ask:

> Is hallucination a problem of missing evidence, failed access, failed integration, or failure of epistemic control?

This could become a major mechanistic-interpretability component of the PhD.

---

# 20. LONG-TERM THESIS STRUCTURE

A possible PhD research program:

## Paper/Study 1 — Phenomenon

**Knowledge Presence vs Knowledge Accessibility in LLMs**

Establish:
- known;
- unknown;
- known-but-inaccessible;
- accessible.

## Paper/Study 2 — Causal Mechanism

**Information-Access Bottlenecks as a Causal Driver of Hallucination**

Manipulate:
- bandwidth;
- communication;
- retrieval;
- access.

## Paper/Study 3 — Mechanistic Analysis

**Where and Why Does Epistemic Access Fail?**

Use:
- activation analysis;
- attention;
- probing;
- causal representation interventions;
- knowledge recall methods.

## Paper/Study 4 — Architecture

**Epistemic Access Architecture**

Implement:
- Reader;
- Epistemic Memory;
- Shared Workspace;
- Arbitration;
- Generator;
- claim verification.

## Paper/Study 5 — Generalization

Evaluate across:
- model families;
- model scales;
- task types;
- long-context;
- domain-specific knowledge;
- conflicting evidence.

---

# 21. HOW TO START — RECOMMENDED ORDER

Do NOT start by training a large new LLM.

Recommended order:

    1. Freeze hypothesis
         ↓
    2. Build literature matrix
         ↓
    3. Operationalize knowledge states
         ↓
    4. Select auditable model/data (e.g. Pythia)
         ↓
    5. Build Pilot Study
         ↓
    6. Run known-vs-inaccessible experiment
         ↓
    7. Run access-block / access-restore experiment
         ↓
    8. Analyze mechanism
         ↓
    9. Build minimal EAA prototype
         ↓
    10. Compare with RAG/Self-RAG/verifier baselines
         ↓
    11. Generalize
         ↓
    12. Write PhD proposal / papers

---

# 22. WHO TO CONTACT

Do not contact dozens of researchers immediately.

Preferred order:

### First: potential PhD supervisor

Target researcher profile:

- LLMs;
- hallucination;
- mechanistic interpretability;
- uncertainty/calibration;
- retrieval/reasoning;
- cognitive architectures.

Contact after there is:
- a 1-page hypothesis;
- a literature matrix;
- a reproducible pilot or preliminary result.

### Second: researchers directly related to auditable knowledge / Pythia

Relevant 2026 work:
- Christopher Adrian Kusuma
- Muhammad Reza Qorib
- Hwee Tou Ng

Reason:
Their work involving Pythia, pretraining data, and knowledge boundaries is directly useful for establishing a clean experimental setting.

The goal of contact:

NOT:
> “I have invented a new theory.”

Instead:

> “Your work provides an experimental substrate for testing a stronger hypothesis about knowledge accessibility versus knowledge presence. I would like to investigate whether access can be manipulated causally.”

### Third: cognitive neuroscience / split-brain expert

Use neuroscience expertise to validate:
- terminology;
- interpretation of split-brain experiments;
- limits of the biological analogy.

Do not ask neuroscience to “prove” the LLM theory.

---

# 23. THE RESEARCH STORY IN ONE PARAGRAPH

Current LLMs primarily integrate epistemic processing and linguistic generation within a predominantly generative mechanism. This can allow plausible language to be produced despite incomplete, inaccessible, or conflicting evidence. Inspired functionally by split-brain research, this research hypothesizes that the gap between knowledge availability and knowledge accessibility is an important contributor to hallucination. The first goal is to test this hypothesis causally by manipulating information access between a knowledge/epistemic subsystem and a generator. The second goal is to determine where access fails. The final goal is to build an integrated Epistemic Access Architecture in which a dedicated reader/epistemic subsystem maintains structured evidence and an arbitration mechanism controls what the generator is epistemically authorized to say.

---

# 24. THE ONE-SENTENCE THESIS

> **Hallucination may arise not only because a language model lacks knowledge, but because knowledge that exists is not reliably accessible or epistemically integrated into the generative process; therefore, separating evidence processing from language generation while preserving controlled information integration may provide a principled architectural path toward more truthful language models.**

---

# 25. CURRENT “NORTH STAR”

Whenever future research directions become confusing, return to this question:

> **If the model already has the relevant knowledge, why does it still hallucinate?**

Then decompose:

    Does the knowledge exist?
          ↓
    Can the system access it?
          ↓
    Can it integrate it?
          ↓
    Does the epistemic state influence generation?
          ↓
    Does the generator remain allowed to guess?
          ↓
    Did hallucination occur?

This decomposition should guide the entire PhD.

---

# 26. IMPORTANT POSITIONING

The intended research is NOT:

- “RAG but better.”
- “A left-brain/right-brain LLM.”
- “A verifier attached to an LLM.”
- “Give the LLM all training data.”
- “Human brain simulation.”

The intended research IS:

- a causal study of knowledge accessibility;
- an epistemic model of hallucination;
- controlled communication between specialized cognitive functions;
- an integrated epistemic–generative architecture;
- an architecture where epistemic state has authority over generation.

---

# 27. NEXT IMMEDIATE TASK

The best next task after reading this file:

## Build Pilot Study #1

Title:

**“Knowledge Presence Does Not Imply Knowledge Accessibility: A Controlled Study of Hallucination in Auditable Language Models.”**

Deliverables:

1. precise operational definitions;
2. dataset construction;
3. Pythia/checkpoint selection;
4. known/unknown/accessible/inaccessible conditions;
5. hallucination evaluation;
6. access manipulation;
7. statistical testing;
8. expected plots;
9. failure/falsification criteria;
10. reproducible code structure.

The assistant should NOT jump directly to the final EAA implementation before this pilot.

---

# 28. RESEARCH PHILOSOPHY

The user wants this to become a serious PhD-level research program.

Therefore future work should prioritize:

- falsifiability over storytelling;
- causal evidence over correlation;
- reproducibility over impressive demos;
- carefully controlled baselines;
- precise operational definitions;
- novelty verified against current literature;
- modest claims until evidence exists.

The split-brain analogy is the inspiration.

**The causal information-access mechanism is the scientific target.**