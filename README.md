# Pharmacophore Creation Strategies: Human vs. Machine

This repository contains the Supplementary Information (SI) and Supporting Scripts for the study: **"Pharmacophore Creation Strategies: Human vs. Machine"**. 

---

## Abstract

<div align="justify">
Pharmacophores are abstract representations of the essential steric and electronic features required for biomolecules to bind to a target of interest. In this study, two strategies are employed for creating small molecule pharmacophore models: one involving humans and chemical intuition, the other a variety of different algorithmic approaches. Virtual screening experiments, using this panel of pharmacophore models, were conducted, and a systematic performance comparison described. It is found that while human-generated models can perform comparably to those created by machine, the machine-generated models are more consistently performative across the targets used in the screening experiment. Three case studies are discussed in detail; these represent examples for which the human-generated model performance is better, comparable to, and worse than their associated machine-generated models. Finally, a consensus ‘Human-in-the-Loop’ strategy is described and evaluated.
</div>

## 📁 Repository Structure

```text
.
├── prepped-complexes/      # Curated protein-ligand structures
├── scripts/                # Python utility and validation scripts
│   ├── mcnemar.py          # Statistical significance testing
│   └── sanity.py           # mlxtend-based cross-validation
├── SI/                     # Supplementary tables (S1.xlsx, S2.xlsx)
└── README.md
```

---

## 🧬 [Prepared Complexes](./prepped-complexes/)

The prepared complexes used for the virtual screening experiments available in both `.moe` and `.pdb` formats.

---

## 💻 [Supporting Scripts](./scripts/)

These utility scripts were used to process the screening data and validate statistical significance.

### 1. `mcnemar.py`
Evaluates the statistical significance between model pairs.
* **Input:** Model prediction arrays.
* **Output:** McNemar Contingency Table, $\chi^2$ (Chi-squared) value, and $p$-value.

### 2. `sanity.py`
A validation script providing a cross-check of the results using the `mlxtend` package to ensure mathematical consistency.

---

## 📁 [Supplementary Information](./SI/)

The following datasets provide the raw results and statistical foundations for the study:

* **S1.xlsx:** Complete virtual screening data as a function of target.
* **S2.xlsx:** McNemar analysis results.
