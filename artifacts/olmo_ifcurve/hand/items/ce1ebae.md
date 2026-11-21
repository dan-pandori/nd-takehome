# Item ce1ebae

## Prompt (as the model received it)

Ensure that stop words constitute no more than 31% of the total words in your response. Design an algorithm to generate unique magic abilities for characters in the world of Aethoria. The algorithm should consider the following:  Each magic ability should have a unique name and description  Magic abilities should be categorized by rank, with higher ranks indicating greater power and rarity  Magic abilities should have unique limitations and costs to balance their power  Overpowered magic should be extremely rare and come with significant consequences  The algorithm should be flexible enough to generate a wide variety of magic abilities, while ensuring that they are balanced and consistent within the world of Aethoria.

## Verifiable constraints

- `ratio:stop_words` {"percentage": 31.0}: followed (official strict checker)

## Answer

To design an algorithm for generating balanced, unique magic abilities in Aethoria while adhering to constraints, follow this structured approach:

### **Algorithm Outline**
1. **Initialization**:  
   - **Parameters**: Define rank (1–5), elemental/school themes (e.g., Pyromancy, Chronomancy), and lore-anchored limits (e.g., mana sources like *Celestial Runes* or *Soul Crystals*).  
   - **Balance Constraints**: Set max "power score" (derived from effect magnitude), cost thresholds, and rarity thresholds (e.g., rank 5 abilities are 0.5% of rank 1 drops in-world).

2. **Step 1: Rank & Category Selection**  
   - **Rank**: Randomly select rank (1–5). High ranks (4–5) trigger rare/consequence checks.  
   - **School/Element**: Assign a primary category (e.g., *Necrotic*, *Spatial Manipulation*). Use a weighted pool favoring common schools (e.g., 60% for basic elements) for lower ranks.  

3. **Step 2: Name Generation**  
   - Combine components from curated lists:  
     - *Adjectives*: "Eclipse," "Voidbinding," "Ethereal"  
     - *Nouns*: "Orb," "Chain," "Requiem"  
     - *Modifiers*: Rank-dependent suffixes (e.g., "-storm" for Rank 3+, "-wraith" for dark magic).  
   - Ensure uniqueness via checksum against a database of existing abilities.  

4. **Step 3: Power & Effect Design**  
   - **Base Effect**: Define the core action (e.g., "ignites targets," "rewinds time").  
     - **Rank Scaling**: Use exponential scaling for magnitude (e.g., Rank 1: affects 1 target; Rank 5: 10-meter radius).  
   - **Secondary Effects**: Randomize 1–2 synergies or trade-offs (e.g., "heals user 10% HP" for pyromancy, "summons shadow doppelgänger" for illusionists).  

5. **Step 4: Cost & Limitations**  
   - **Costs**: Hybrid metrics (mana, health, items):  
     - Rank 1: 2–5 **mana**; Rank 5: 20+ **mana** + 10% max HP or a *rare component* (e.g., *Shard of the Void*).  
   - **Limitations**: Assign 2–3 balanced penalties:  
     - *Physical*: "Reduces stamina by 30% for 1 hour."  
     - *Environmental*: "Ineffective in sunlight (light-based magic)."  
     - *Rarity*: "Requires alignment with lunar eclipses."  
   - **Overpowered Checks (Rank ≥4)**:  
     - 3% chance to trigger a *drawback* (e.g., "user ages 1d4 years," "attracts abyssal leeches").  

6. **Step 5: Consequences for OP Abilities**  
   - If an ability exceeds predefined "power-to-cost" ratios (e.g., 50% above rank norm):  
     1. Impose *permanent* drawbacks (e.g., "–5 to intelligence permanently").  
     2. Trigger narrative flags (e.g., "marked by the Shadow Court," "risk of soul corruption").  

7. **Validation & Balancing**  
   - **Automated Checks**:  
     - Reject abilities with >31% stop words in description (via NLP).  
     - Ensure effect linguistics align with Aethoria’s lore (e.g., no "time travel" without chronomancy laws).  
   - **Iteration**: Regenerate invalid abilities until compliance.  

---

### **Example Output (Rank 4: Spatial Distortion)**  
- **Name**: *Eventide Shift*  
- **Effect**: "Unleash a localized singularity to teleport allies within 10m, or disintegrate non-living matter."  
- **Cost**: 18 mana + 15% max HP.  
- **Limitations**:  
  - "Cooldown: 1 day."  
  - "Alignment required with lunar nodes (every 14 days)."  
  - "User suffers +2 levels of fatigue post-cast."  
- **Consequence (if adjusted to Rank 5)**: "User’s physical form flickers between dimensions for 24 hours; -10 AC."  

---

### **Key Mechanics for Flexibility & Consistency**  
- **Modular Components**: Swap schools/effects via modular code blocks.  
- **Lore Anchors**: Tie mana sources/limitations to in-world geography (e.g., *Runes from the Skyforge Mountains*).  
- **Rare Drops System**: Higher-rank abilities spawn only in specific zones with low frequency (e.g., *Eclipse Dungeons*).  

This ensures variety while maintaining balance and narrative cohesion, adhering to stop-word constraints by prioritizing concise, vivid descriptions.
