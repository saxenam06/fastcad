# Research index

All research was done 2026-09-15 to 2026-09-16 by background research agents, using web search, arXiv, GitHub, vendor sites and LinkedIn. Each document below records one agent's findings, keeps its sources, and marks its inferences.

| Document | Question it answers | Headline |
|---|---|---|
| [linkedin-posts.md](linkedin-posts.md) | What do the 16 LinkedIn posts the user shared actually show? | The AI-CAD copilot wave: LLM agents driving CAD APIs, and demands for exact, editable B-rep rather than meshes. In the posts that stake out a position, AI proposes while deterministic engines build and check. Four posts are off-topic. |
| [methods-landscape.md](methods-landscape.md) | Which academic and open-source methods could power fastcad? | No published method can generate or regenerate a casting of about 2,000 faces. Learned generators stop at about 30–100 faces, and their validity collapses as complexity rises. What works is a typed feature DSL, a deterministic B-rep kernel, CP-SAT, FE and casting checks, and plausibility scoring. |
| [industry-practice-dfm-vendors.md](industry-practice-dfm-vendors.md) | How does industry vary housings? What are the casting rules? Who are the vendors? | Industry freezes the skeleton of interfaces and varies the structure. The casting rules can be written as executable checks. Nobody publicly generates foundry-valid variants of large castings, and almost nobody reports results in gear-engineer terms. |
| [paper-reviews.md](paper-reviews.md) | How do the 21 papers, repos and benchmarks the user sent compare with our approach? | None edits a production B-rep under frozen interfaces, casting rules and a copied FE deck. Their evidence supports our rule of no code generation at runtime. Many of their ideas are worth adopting. |
| [platforms-and-kernels.md](platforms-and-kernels.md) | Can commercial CAD platforms and kernels do our operations better than OpenCascade? | Every mainstream CAD platform runs on one of four kernels; Onshape, SolidWorks and NX all use Parasolid. OpenCascade's documented fillet and defeaturing limits hit our housing. Onshape is the cloud option: strong direct editing, but API allowances per user and data held in the cloud. CGM is the local commercial option. No platform exports face names in STEP. The M0 bake-off decides, behind an operator layer that works on any kernel. |
| [startups-and-ntop.md](startups-and-ntop.md) | Where do the AI-CAD startups stand, and is nTop's 70–80% claim true? | No verified startup makes variants of existing production CAD with casting design rules and FE analysis. The strongest threats are Synera, nTop, Neural Concept, PhysicsX and DEP MeshWorks. nTop's figure is anecdotal and about regeneration, so we publish our own yield funnel instead. SimScale's structural analyses run on Code_Aster, the same solver as our deck, and it is a partner candidate. |

Related:
- [../prior-work/fastcae-and-agenticcae.md](../prior-work/fastcae-and-agenticcae.md): what we already have.
- The GRC documents in [../grc/](../grc/).
- The combined positioning in [../fastcad-positioning.md](../fastcad-positioning.md).
