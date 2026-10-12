# Artificial Intelligence Portfolio

**Siddharth Barjatya** · Dunedin, New Zealand · [LinkedIn](https://www.linkedin.com/in/siddharth-barjatya/)

Selected academic projects from my Master of Applied Science with Distinction in Artificial Intelligence at the University of Otago (cumulative GPA 8.7/9). Each project folder holds a README that explains the problem, the approach and the results, together with the project report and, where available, the source code.

## Selected Academic Projects

| Project | What it solves | Techniques |
|---|---|---|
| [GPT-Style Transformer for Language Modelling](gpt-transformer-language-modelling) | Predicts the next token of Shakespeare text and generates new passages in the same style, using a decoder-only transformer written from scratch. | Multi-head causal self-attention, positional embeddings, pre-norm residual blocks, automated tests for attention properties, 50+ hyperparameter runs |
| [Computer Vision: Classification, Segmentation & Generative Diffusion](computer-vision-classification-segmentation-diffusion) | Classifies flower images into four groups, outlines the flower in each image pixel by pixel, and generates new flower images from noise. | VGG16-style CNN, U-Net, timestep-conditioned diffusion model (DDPM), class-imbalance sampling |
| [Deep Reinforcement Learning for Atari Space Invaders](deep-reinforcement-learning-space-invaders) | Trains an agent to play Space Invaders from raw screen pixels. | Deep Q-Network, experience replay, target network, epsilon-greedy exploration, PyTorch, Gymnasium/ALE |
| [Large-Scale Information Retrieval & Graph Database Systems](information-retrieval-and-graph-databases) | Searches and analyses a corpus of more than 170,000 Wall Street Journal articles. | BM25 ranking, custom binary inverted index in R, Neo4j property graph, Cypher |
| [Adversarial Search & Evolutionary Agents](adversarial-search-and-evolutionary-agents) | Builds game-playing agents for a card game with hidden information and for a multi-agent Snake game. | Minimax with alpha-beta pruning, genetic algorithms, neuroevolution |

## Repository Layout

```
.
├── gpt-transformer-language-modelling/
├── computer-vision-classification-segmentation-diffusion/
├── deep-reinforcement-learning-space-invaders/
├── information-retrieval-and-graph-databases/
│   ├── bm25-search-engine-in-r/
│   └── neo4j-graph-database/
└── adversarial-search-and-evolutionary-agents/
    ├── xnimmt-minimax-alpha-beta-agent/
    └── snake-genetic-algorithm-neuroevolution/
```

## Notes

- Each `project-report.pdf` is the write-up submitted for that project, so it also shows the experiments and results in full.
- Source code is included for the minimax agent and the BM25 search engine. For the other projects this repository holds the report and README.
- Datasets and course-supplied game frameworks belong to their owners and are not redistributed here.
- My professional machine learning work at MastaPlex is covered by a confidentiality agreement, so it is not part of this repository. It is described on my [LinkedIn profile](https://www.linkedin.com/in/siddharth-barjatya/).
