---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - blier2018description
---

# Blier & Ollivier (2018), "The Description Length of Deep Learning Models" (NeurIPS 2018)

Source: arXiv 1802.07044v5 (full text read: §1–5, App. D–E).

## Paper claims
- **Prequential code (Def. 3, §3.4, eq. 3.6).** L_preq = t₁·log₂K + Σ_s −log₂ p_θ̂(t_s)(y over block s+1). The first block uses the uniform code, and every later block is coded by a model retrained on all earlier blocks. "The difference between the prequential codelength … and the log-loss … of the final trained model, can be interpreted as the amount of information that the trained parameters contain about the data" (§3.4).
- **Table 1 (kbits of label information; compression ratio vs uniform; test accuracy):**
  - MNIST: uniform 199 (ratio 1). Float32 two-part code > 8.6 Mbits. Variational 22.2 (0.11). Prequential **4.10 (0.02), 99.5 %**.
  - CIFAR-10: uniform 166. Variational 89.0 (0.54). Prequential **45.3 (0.27), 93.3 %**. Switch code 34.6 (Table 2).
- Prequential coding "yields much better codelengths than variational inference". On MNIST it is 6× shorter than the variational code, and on CIFAR 2× shorter (§3.4).
- **Catch-up phenomenon (§3.4).** VGGb needs "5,000 samples on CIFAR to reach a cumulative compression ratio < 1, even though the encoding cost per label becomes drops below uniform after just 1,000 samples". Switching between models (App. E) fixes this, "even when just switching between copies of the same model with different SGD stopping times".
- **Asymptotics (§4).** Under strong regularity assumptions, two-part, Bayesian and prequential codes all give n·H(Y|X) + (d/2)·log₂ n + O(1) (BIC), "Hence there was no obvious reason for the prequential code to be an order of magnitude better than the others". Deep nets do not meet these assumptions. "The number of parameters is not an obstacle to compression" (§4). The paper does not evaluate the BIC term numerically. The comparison below is mine.
- Prequential codes "depend on the performance of the underlying training algorithm" (§3.4). VGGa vs VGGb (same architecture, different training procedure) differ substantially (Fig. 2).
- **Block boundaries (App. D).** MNIST: 8, 16, …, 32,768. CIFAR: 10, 20, …, 40,960 (doubling).

## Evidence
Two image-classification datasets, 3–5 architectures each, Adam at learning rate 1e−3, dropout. The best model per dataset is reported.

## Our interpretation
- B2 follows this design: doubling blocks, a uniform first block, and a fresh model per block. The run's "absorbed bits" is exactly the §3.4 difference.
- B2 trains three sizes (S/M/L). A **switch code** that picks the best size per block costs at most log₂3 ≈ 1.6 bits per block to signal. It directly addresses catch-up, the risk that L pays more than uniform on the first 64–256 theorems.
- The BIC term is a useful *upper* reference only. For 9.56 M parameters and n ≈ 1.7 × 10⁷ (state, action) pairs, (d/2)·log₂ n ≈ 4.78 × 10⁶ × 24 ≈ 1.1 × 10⁸ bits (my arithmetic). On MNIST the prequential total (4.10 kbits) is far below any parameter-count term: even the float32 two-part code exceeds 8.6 Mbits (Table 1). This suggests real deep-net codes fall far below the BIC reference (my inference).

## Limits
Labels only (10 classes), i.i.d. data, image tasks. No algorithmic or sequence task and no transformer. The reported numbers are the minimum over models and hyperparameters (a selection effect, small in bits).
