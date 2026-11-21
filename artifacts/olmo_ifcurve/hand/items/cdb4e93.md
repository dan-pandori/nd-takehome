# Item cdb4e93

## Prompt (as the model received it)

A spring pendulum with mass m on a spring with stiffness k, performing undamped harmonic oscillations, has at the initial moment of time t = 0 the coordinate x = x0 and velocity V =V0. What will be the amplitude and initial phase of these oscillations? Formulas only Your response must include bullet points denoted by * and at least one sub-bullet point denoted by - for each bullet point.

## Verifiable constraints

- `format:sub-bullets` {}: followed (official strict checker)

## Answer

* Amplitude \( A \):  
  - \( A = \sqrt{x_0^2 + \left( \dfrac{V_0}{\omega} \right)^2} \)  
    - \( \omega = \sqrt{\dfrac{k}{m}} \)  

* Initial phase \( \phi \):  
  - \( \phi = \arctan\left( \dfrac{x_0 \omega}{V_0} \right) \)  
    - Alternatively, \( \phi = \arctan2\left( x_0 \omega, V_0 \right) \) for quadrant accuracy.
