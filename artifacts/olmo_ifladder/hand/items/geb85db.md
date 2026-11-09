# Item geb85db

## Prompt (as the model received it)

Claim: When you download a model from Huggingface or train one yourself, the file contains a collection of vectors. There is nothing else in the file (edit: there's often some metadata used to identify the model.) Those vectors are the constant weights in a very large equation. The equation itself is actually not fixed. You can select from a variety of activation functions when you use a model, and each activation function will modify how those weights impact the result.  Task: Evaluation the above claim for accuracy. Write a paragraph using words that contain only three types of vowels. The response should include at least 4 pronouns.

## Verifiable constraints

- `words:vowel` {}: followed (official strict checker)
- `count:pronouns` {"N": 4.0}: followed (official strict checker)

## Answer

it is near right that nets have weights. they keep a few details. while the math is fixed. each part has set steps. they need fit the shape. i believe.
